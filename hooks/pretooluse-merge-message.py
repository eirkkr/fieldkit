#!/usr/bin/env python3
"""PreToolUse hook: refuse a squash merge whose commit message breaks the kit's rules.

The kit squash-merges, so the only commit a PR leaves on the default branch is
the one `gh pr merge --subject ... --body ...` writes. This hook checks that
message before the merge runs: the subject's type, case, length and ` (#N)`
suffix, and the body's wrapping - the rules in conventions.py, next to this
file. A body-only merge, or one whose subject the shell rewrites, gets only
the credit check below.

The body is read from `--body`/`-b`, or from `--body-file`/`-F` naming a file
or `-` fed by a heredoc (a `--body "$(cat <<'EOF' ...)"` counts as one). With
no `--subject`, GitHub builds the subject from the PR title, which CI checks
instead. The PR number comes from a numeric or URL argument; otherwise any
` (#N)` is accepted.

It also refuses a message lacking the `Co-authored-by` line for each commit
author who isn't the PR's author (git.md's Squash credit rule), whenever the
command gives a subject or a body. That needs the PR's authors, so it asks
`gh pr view` - the one call every checked merge pays - and, for a PR of 100
commits or more, pages through the REST commit list. A refusal makes one more
call, `gh api users/<login>`, per missing author, to spell out the line.

In a repo that reaches the kit, a `gh pr merge` the hook can't check is
refused, not let through: a squash commit can't be amended, so an unchecked
merge is the worse outcome (ADR 074). That covers a lookup that fails, times
out or is unreadable; a body the shell rewrites (an unquoted heredoc, a
`$VAR`) or a file that can't be read; a merge that reads a heredoc in a
command whose heredocs can't be matched to their `<<` operators; a payload
directory that doesn't exist; a merge in a string a shell runs (after
`bash -c`, or `eval`'s words); and a merge with a `GH_` or `GITHUB_` variable
set on it or exported before it, which the hook's own lookup wouldn't see; a
repo `git` can't be asked about (missing, slow, refused); a command the lexer
rejects (an unbalanced quote) that mentions `gh` and `merge`; and a command
that moves among more than 8 possible directories, in any repo. `cd`, `pushd`
and `popd` are followed, and a merge is checked in each directory it might run
in when a subshell's `cd`, `cd -` or a move the hook can't read leaves that
unclear. A
crash in the check refuses the merge in any repo, since by then the hook can't
tell which repo it is in. A `gh pr merge` is found after `FOO=1`, `env`,
`command`, `time`, `sudo`, `!`, `{`, `then` or a path to `gh`, and
`-R`/`--repo` may come before `pr` or `merge`. A merge through `gh api`, built
from a variable, or fed to a shell on stdin, is not recognised (ADR 074).

Like the branch-name hook it applies only in a repo that reaches the kit and
refuses through PreToolUse's JSON `deny`. See ADR 047 and ADR 074 under
docs/decisions/.

Registered in ~/.claude/settings.json by `just install`
(scripts/register-hooks.sh); not meant to be invoked directly. Standard
library only.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from typing import NamedTuple

from conventions import kit_status, message_problems, message_reason, parse_command

# Every `gh pr merge` flag that takes a value, so a value is never read as the PR.
# A short flag's value may follow it, or follow `=`, or be joined to it (`-bTEXT`).
_LONG_VALUE_FLAGS = frozenset(
    {"--subject", "--body", "--body-file", "--repo", "--match-head-commit", "--author-email"}
)
_SHORT_VALUE_FLAGS = {"t": "--subject", "b": "--body", "F": "--body-file", "R": "--repo", "A": "--author-email"}

# `GH_REPO=...` or `GITHUB_TOKEN=...` set on the command: it changes which repo or
# account `gh` uses, and the hook's own lookup would run without it.
_GH_ENVIRONMENT = re.compile(r"(?:GH|GITHUB)_[A-Z_]+=")

# A `$name`, `${...}`, `$(...)`, `$'...'` or backtick: the shell rewrites the
# value first. A word has lost its quotes by the time it is tested, so a
# single-quoted `'$X'` is flagged too; `$1`, `$?` and `$$` are not.
_EXPANSION = re.compile(r"\$[({A-Za-z_']|`")
# `$(cat <<'EOF'` with its body cut out of the command: the usual way to pass a body.
_CAT_HEREDOC = re.compile(
    r"\$\(\s*cat\s+<<-?\s*(?:['\"][^'\"\n]+['\"]|\\?[A-Za-z_][^\s'\"\\<>|&;()$`]*)\s*\)"
)
# What `--body-file` may name in place of a heredoc: the hook's own stdin isn't it.
_STDIN_PATHS = frozenset({"-", "/dev/stdin", "/dev/fd/0", "/proc/self/fd/0"})

# Shells that run a string as a command, where `gh pr merge` may be hiding.
_SHELLS = frozenset({"bash", "sh", "zsh", "dash", "eval"})

# A trailer line is `Token: value` or an indented continuation. Git reads
# trailers in a last paragraph made of them; this is stricter than git, which
# also takes a mixed paragraph holding a known trailer such as `Signed-off-by`,
# and looser, in letting a subject line count as one.
_TRAILER_LINE = re.compile(r"[A-Za-z][A-Za-z0-9-]*:[ \t]+\S.*|[ \t]+\S.*")
# A co-author in a commit message, by GitHub's no-reply address, which names the login.
_NOREPLY_TRAILER = re.compile(
    r"^Co-authored-by:.*<\d+\+([A-Za-z0-9-]+(?:\[bot\])?)@users\.noreply\.github\.com>", re.IGNORECASE | re.MULTILINE
)

# Seconds one `gh` lookup may take, and all the lookups for one `gh pr merge`
# together: past either the lookup counts as failed and the merge is refused.
_GH_TIMEOUT = 15
_GH_TOTAL = 25

# `gh pr view --json commits` returns at most this many commits. A PR with that
# many is read again from the REST list, which GitHub caps at the second number.
_COMMIT_PAGE = 100
_COMMIT_CAP = 250

# Variables that make `gh` colour its JSON, which then won't parse.
_COLOUR_VARS = ("CLICOLOR_FORCE", "GH_FORCE_TTY")


# A `cd` option (`-P`, `-L`, `-e`, `-@`); a lone `-` is `cd -`'s argument.
_OPTION = re.compile(r"-[A-Za-z@]+")

# A command that mentions both words, which the hook refuses when it can't parse it.
_MENTIONS_MERGE = re.compile(r"\bgh\b[\s\S]*\bmerge\b")


class Unreadable(Exception):
    """A `gh pr merge` whose body, or whose directory, the hook can't read."""


class LookupFailed(Exception):
    """The PR's authors couldn't be read; the message says why.

    `permanent` marks a cause no retry of the command can cure.
    """

    def __init__(self, detail, permanent=False):
        super().__init__(detail)
        self.permanent = permanent


class Message(NamedTuple):
    """What a `gh pr merge` would write.

    `subject` is the subject to lint, None where the command gives none or the
    shell rewrites it; `text` is the whole message, the part the credit check
    reads; `selector` is None where the command names no PR.
    """

    pr: str
    subject: str | None
    text: str
    selector: str | None
    repo: str | None


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str):
        return

    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    parsed, found, matched, complete = parse_command(command)
    exported = False
    here = Directories(cwd)
    for words, numbers, nested in parsed:
        if here.follow(words, nested):
            continue
        if words[:1] in (["export"], ["declare"], ["typeset"], ["readonly"]):
            exported = exported or any(_GH_ENVIRONMENT.match(word) for word in words[1:])
            continue
        merge = merge_arguments(words) or embedded_merge(words)
        if merge is None and not hides_merge(words):
            continue
        if here.overflow:
            deny(too_many_directories_reason())
            return
        for directory in here.possible:
            try:
                if merge is None:
                    reason = unrecognised_reason(directory, "inside a string a shell runs")
                elif exported or any(_GH_ENVIRONMENT.match(word) for word in words):
                    reason = unrecognised_reason(directory, "with a `GH_` or `GITHUB_` variable set on it or exported before it")
                else:
                    own = [found[number] for number in numbers] if matched else None
                    reason = check_merge(*merge, own, directory)
            except Exception:  # noqa: BLE001 - registered `|| true`, so a crash would let the merge through
                reason = crash_reason()
            if reason:
                deny(reason)
                return
    if not complete and _MENTIONS_MERGE.search(command):
        for directory in here.possible:
            try:
                reason = unrecognised_reason(directory, "in a command the hook can't parse (an unbalanced quote)", _UNBALANCED_FIX)
            except Exception:  # noqa: BLE001 - as above
                reason = crash_reason()
            if reason:
                deny(reason)
                return


# The most directories the hook tracks as possible. Past it the hook refuses a merge, whatever repo it is in.
_MAX_DIRECTORIES = 8
# Words a command may begin with before `cd`: the keywords of a block, and the builtins that run it.
_BEFORE_CD = ("{", "then", "do", "else", "!", "builtin", "command")


class Directories:
    """Where the command may be running, as `cd`, `pushd` and `popd` move it.

    `possible` is every directory the next command could run in, by real path.
    It is one unless the hook can't tell: a `cd` in a subshell (parentheses, a
    pipeline, `&`) leaves the old directory in as well, and so do `cd -`, a
    `pushd` or `popd` the hook can't follow, and a `cd` it can't read. A merge
    is checked in each. A `cd` to a target the hook can't expand (`$(...)`, an
    unset variable) or a directory that isn't there changes nothing. Past
    `_MAX_DIRECTORIES` the hook gives up: `overflow` is set.
    """

    def __init__(self, start):
        self.possible = [os.path.realpath(start)]
        self.seen = list(self.possible)
        self.stack = []
        self.overflow = False

    def follow(self, words, nested):
        """Move on `words` if it is a directory change, returning whether it was one."""
        while words and words[0] in _BEFORE_CD:
            words = words[1:]
        if not words or words[0] not in ("cd", "pushd", "popd"):
            return False
        options = [w for w in words[1:] if _OPTION.fullmatch(w)]
        args = [w for w in words[1:] if w != "--" and w not in options]
        try:
            if words[0] != "cd" and (options or any(a.startswith("+") for a in args)):
                # `pushd -n`, `popd -n` and `pushd +N` move the stack, not the directory, or rotate it.
                self._unknown()
            else:
                self._follow(words[0], args, nested)
        except Exception:  # noqa: BLE001 - a target `expanduser` chokes on (a NUL byte, a lone surrogate) is one we can't follow
            self._unknown()
        return True

    def _follow(self, name, args, nested):
        if name == "popd":
            if args:
                self._unknown()
            elif nested:
                self._unknown()
            elif self.stack:
                self._move(self.stack.pop(), False)
            return
        if len(args) > 1 or (name == "pushd" and not args):
            # `pushd` with no argument swaps the top two entries, `pushd +N` rotates, and more words are an error.
            self._unknown()
        elif args == ["-"]:
            self._unknown()
        else:
            target = args[0] if args else "~"
            moved = [self._resolve(d, target) for d in self.possible]
            if name == "pushd" and not nested and moved != self.possible:
                self.stack.append(list(self.possible))
            elif name == "pushd" and nested:
                self._unknown()
                return
            self._move(moved, nested)

    @staticmethod
    def _resolve(directory, target):
        target = os.path.expandvars(os.path.expanduser(target))
        if "$" in target or "`" in target:
            return directory
        path = os.path.realpath(os.path.join(directory, target))
        return path if os.path.isdir(path) else directory

    def _unknown(self):
        """A change the hook can't follow: everywhere it has been is possible."""
        self._move(list(self.seen), True)

    def _move(self, directories, nested):
        # In a subshell the old directory is still where the command after `)` runs.
        wanted = self.possible + directories if nested else directories
        self.possible = list(dict.fromkeys(wanted)) or self.possible
        self.seen = list(dict.fromkeys(self.seen + self.possible))
        if len(self.possible) > _MAX_DIRECTORIES or len(self.seen) > _MAX_DIRECTORIES:
            self.overflow = True
            del self.possible[_MAX_DIRECTORIES:], self.seen[_MAX_DIRECTORIES:]


def merge_arguments(words):
    """The (arguments after `pr merge`, repo named before `merge`) of a `gh pr merge`, or None.

    The words begin with `gh`. Its own `-R`/`--repo` may sit before `pr` or
    between `pr` and `merge`, where it names the repo as the flag after
    `merge` does.
    """
    index = 0
    repo = None
    for word in ("gh", "pr", "merge"):
        if words[index : index + 1] != [word]:
            return None
        index += 1
        if word != "merge":
            skipped = skip_flags(words, index, repo)
            if skipped is None:
                return None
            index, repo = skipped
    return words[index:], repo


def skip_flags(words, index, repo):
    """The (index past the flags at `index`, repo they name) between `gh`, `pr` and `merge`, or None."""
    while index < len(words) and words[index].startswith("-"):
        flag, sep, inline = words[index].partition("=")
        index += 1
        if flag in ("--repo", "-R"):
            if sep:
                repo = inline
            elif index < len(words):
                repo = words[index]
                index += 1
            else:
                return None
        elif not flag.startswith("--") and flag.startswith("-R"):
            repo = flag[2:] or None
    return index, repo


def embedded_merge(words):
    """The `merge_arguments` of a `gh pr merge` that follows other words, or None.

    `FOO=1 gh pr merge`, `env FOO=1 gh pr merge`, `command gh pr merge`,
    `time gh pr merge`, `sudo gh pr merge`, `! gh pr merge`, `{ gh pr merge ...`,
    `then gh pr merge ...` and `/usr/bin/gh pr merge` all run the merge.
    """
    for position, word in enumerate(words):
        if os.path.basename(word) == "gh":
            merge = merge_arguments(["gh", *words[position + 1 :]])
            if merge:
                return merge
    return None


def hides_merge(words):
    """Whether a command hides a `gh pr merge` in a string a shell runs.

    That is the string after `-c` of `bash`, `sh`, `zsh` or `dash`, or the
    words of `eval`, wherever in the command they come (`env bash -c '...'`,
    `timeout 600 bash -c '...'`). Each is parsed as a command of its own and
    searched the way a direct command is, so `bash -c 'GH_REPO=x /usr/bin/gh pr
    merge ...'` is found, and a quoted message that only says it is not. A
    script (`bash run.sh`) is not looked into.
    """
    for position, word in enumerate(words):
        shell = os.path.basename(word)
        if shell not in _SHELLS:
            continue
        rest = words[position + 1 :]
        if shell != "eval":
            flags = [index for index, arg in enumerate(rest) if re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", arg)]
            if not flags:
                continue
            rest = rest[flags[0] + 1 :]
        candidates = [rest]
        for arg in rest:
            parsed, _, _, complete = parse_command(arg)
            candidates += [inner for inner, _, _ in parsed]
            if not complete and _MENTIONS_MERGE.search(arg):
                return True
        if any(merge_arguments(c) or embedded_merge(c) for c in candidates):
            return True
    return False


def kit_doc(cwd):
    """git.md's path as the repo at `cwd` reaches it, or None. Raises Unreadable if `cwd` isn't a directory."""
    if not os.path.isdir(cwd):
        raise Unreadable(f"the directory `{cwd}` doesn't exist, so the hook can't tell which repo the merge is for")
    doc, trouble = kit_status(cwd)
    if trouble:
        raise Unreadable(f"{trouble}, so the hook can't tell whether the repo reaches the kit")
    return doc


def check_merge(args, repo, own_heredocs, cwd):
    """The refusal for one `gh pr merge`'s arguments, or None to let it through.

    `own_heredocs` is the (body, quoted, delimiter) of each heredoc the merge's own command opens,
    or None when the command's heredocs can't be matched to its `<<` operators.
    """
    try:
        doc = kit_doc(cwd)
    except Unreadable as error:
        return unreadable_reason(str(error), "conventions/git.md")
    if not doc:
        return None
    try:
        message = merge_message(args, repo, own_heredocs, cwd)
    except Unreadable as error:
        return unreadable_reason(str(error), doc)
    if message is None:
        return None
    reasons = []
    if message.subject is not None:
        problems = message_problems(message.text, message.pr)
        if problems:
            reasons.append(message_reason(problems, doc))
    try:
        missing, id_failure = missing_credit_lines(message.text, message.selector, message.repo, cwd)
    except LookupFailed as error:
        reasons.append(lookup_reason(error, doc))
    else:
        if missing:
            reasons.append(credit_reason(missing, doc, id_failure))
    return "\n\n".join(reasons) or None


_DIRECT_FIX = (
    "Run it as a plain "
    "`gh pr merge <PR> --squash --subject ... --body-file -` command, not through `bash -c` or `eval`, "
    "and name another repo with `-R owner/repo`, not a `GH_` variable."
)
_UNBALANCED_FIX = (
    "Balance its quotes (a quote left open, or `$'...'` with an escaped quote inside) and run it as a plain "
    "`gh pr merge <PR> --squash --subject ... --body-file -` command."
)


def too_many_directories_reason():
    """The refusal for a command that moves among more directories than the hook tracks."""
    return (
        f"This command changes directory so many ways (more than {_MAX_DIRECTORIES} possible directories) that "
        "the hook can't tell which repo its `gh pr merge` runs in, and a squash commit can't be amended once "
        "merged. Split it: `cd` to the repo in one command, then run the merge on its own."
    )


def unrecognised_reason(cwd, how, fix=_DIRECT_FIX):
    """The refusal for a `gh pr merge` the hook can't check, run `how`, or None outside the kit."""
    try:
        doc = kit_doc(cwd)
    except Unreadable as error:
        return unreadable_reason(str(error), "conventions/git.md")
    if not doc:
        return None
    return (
        f"This command runs `gh pr merge` {how}, so the hook can't check the squash message, and a squash "
        f"commit can't be amended once merged. {fix} See {doc}."
    )


def merge_message(args, repo, own_heredocs, cwd):
    """The Message a `gh pr merge` would write, or None.

    `repo` is the one given before `merge`, unless a flag names another. None
    when the command gives neither subject nor body - GitHub then builds the
    message, and CI checks the PR title - or when a flag has no value, which
    `gh` refuses itself. Raises Unreadable for a body the hook can't read.
    """
    subject = body = selector = None
    pr = "any"
    index = 0
    while index < len(args):
        arg = args[index]
        index += 1
        if arg.startswith("--"):
            flag, sep, inline = arg.partition("=")
            if flag not in _LONG_VALUE_FLAGS:
                continue
            value = inline if sep else None
        elif arg.startswith("-"):
            flag, value = short_flag(arg)
            if flag is None:
                continue
        else:
            selector = arg
            number = re.fullmatch(r"#?(\d+)|.*/pull/(\d+)/?", arg)
            if number:
                pr = number[1] or number[2]
            continue
        if value is None:
            if index >= len(args):
                return None
            value = args[index]
            index += 1
        if flag == "--subject":
            subject = value
        elif flag == "--body":
            body = read_body(value, own_heredocs)
        elif flag == "--repo":
            repo = value
        elif flag == "--body-file":
            body = read_body_file(value, own_heredocs, cwd)
    if subject is None and body is None:
        return None
    if subject is None:
        text = body
    else:
        text = f"{subject}\n\n{body}" if body else subject
    lintable = None if subject is None or _EXPANSION.search(subject) else subject
    return Message(pr, lintable, text, selector, repo)


def short_flag(arg):
    """The (long flag, joined value or None) of a short-flag cluster such as `-sbTEXT`, else (None, None).

    The boolean flags (`-s`, `-m`, `-r`, `-d`) can be bundled before a
    value-taking one; whatever follows that one is its value, as in `gh`'s own
    parser, with a leading `=` dropped. A boolean flag given a value (`-d=true`)
    ends the cluster: what follows the `=` is not another flag.
    """
    for position, letter in enumerate(arg[1:], start=1):
        flag = _SHORT_VALUE_FLAGS.get(letter)
        rest = arg[position + 1 :]
        if flag:
            return flag, (rest[1:] if rest.startswith("=") else rest) or None
        if rest.startswith("="):
            return None, None
    return None, None


def read_body(value, own_heredocs):
    """A `--body`'s text, taking a `$(cat <<'EOF' ...)` from the command's heredoc."""
    if _CAT_HEREDOC.fullmatch(value):
        return heredoc_text(own_heredocs, "`--body` takes its text from a heredoc")
    if _EXPANSION.search(value):
        raise Unreadable("`--body` holds a shell expansion")
    return value


def read_body_file(path, own_heredocs, cwd):
    """A `--body-file`'s text - the command's heredoc for `-` - or raise Unreadable."""
    if path in _STDIN_PATHS:
        return heredoc_text(own_heredocs, f"`--body-file {path}` reads a heredoc")
    if _EXPANSION.search(path) or path.startswith("~"):
        raise Unreadable(f"`--body-file {path}` holds a path the shell expands, which the hook can't follow")
    full = os.path.join(cwd, path)
    if not os.path.isfile(full):
        raise Unreadable(f"`--body-file {path}` isn't a file the hook can open (it may be created by this same command)")
    try:
        with open(full, encoding="utf-8") as handle:
            return handle.read()
    except UnicodeDecodeError:
        raise Unreadable(f"`--body-file {path}` isn't UTF-8 text") from None
    except OSError as error:
        raise Unreadable(f"`--body-file {path}` can't be opened ({error.strerror})") from None


def heredoc_text(own_heredocs, what):
    """The text of the one heredoc a merge reads its body from, or raise Unreadable."""
    if own_heredocs is None:
        raise Unreadable(
            f"{what}, but the hook can't match this command's heredocs to their `<<` operators (an arithmetic "
            "`<<`, a `<<` in a comment, or a delimiter it doesn't read); write the body as "
            "`--body-file - <<'EOF'` on the merge command"
        )
    if len(own_heredocs) != 1:
        raise Unreadable(f"{what}, but the merge command opens {len(own_heredocs)} heredocs, not one")
    body, quoted, _ = own_heredocs[0]
    if not quoted and _EXPANSION.search(body):
        raise Unreadable(f"{what}, and it is unquoted, so the shell expands its `$` and backticks; write `<<'EOF'`")
    return body


def missing_credit_lines(text, selector, repo, cwd):
    """The (`Co-authored-by` lines `text` lacks, why an id lookup failed or ""). Raises LookupFailed.

    A line's id comes from `gh api users/<login>`, one call per missing
    author; where that fails the line carries `<id>` and the cause is returned.
    """
    deadline = time.monotonic() + _GH_TOTAL
    view = ["pr", "view", *([selector] if selector else []), *(["-R", repo] if repo else [])]
    raw = gh(cwd, deadline, *view, "--json", "author,commits,url")
    try:
        data = json.loads(raw)
        author = data["author"]["login"]
        commits = data["commits"]
        commit_authors = [a for commit in commits for a in commit["authors"]]
        url = data.get("url")
    except (ValueError, KeyError, TypeError, AttributeError):
        raise LookupFailed("its output wasn't the JSON the check expects") from None
    if len(commits) >= _COMMIT_PAGE:
        commit_authors += paged_commit_authors(cwd, deadline, url)
    if not isinstance(author, str) or not author:
        raise LookupFailed("the PR's author has no login (a deleted account?)", permanent=True)
    if not all(isinstance(a, dict) and isinstance(a.get("login") or "", str) for a in commit_authors):
        raise LookupFailed("a commit author wasn't the shape the check expects", permanent=True)
    lines = []
    id_failure = ""
    for login in credited_authors(author, commit_authors, text):
        try:
            found = gh(cwd, deadline, "api", f"users/{login}", "-q", ".id").strip()
        except LookupFailed as error:
            found = ""
            id_failure = id_failure or str(error)
        user_id = found if found.isdigit() else "<id>"
        lines.append(f"Co-authored-by: {login} <{user_id}+{login}@users.noreply.github.com>")
    return lines, id_failure


def paged_commit_authors(cwd, deadline, url):
    """The commit authors of a PR with a full page of commits, from the REST list.

    `gh pr view` has already given the first page, with each commit's
    co-authors; the REST list gives each commit's author, and the co-authors
    named by a no-reply address in its message. A bot account (`name[bot]`) is
    left out, as `gh pr view` gives it no login.
    """
    match = re.fullmatch(r"https://([^/]+)/([^/]+)/([^/]+)/pull/(\d+)", url) if isinstance(url, str) else None
    if not match:
        raise LookupFailed(f"a PR of {_COMMIT_PAGE} commits or more needs its URL, to page through the rest", True)
    host, owner, name, number = match.groups()
    raw = gh(
        cwd,
        deadline,
        "api",
        "--hostname",
        host,
        "--paginate",
        f"repos/{owner}/{name}/pulls/{number}/commits",
        "--jq",
        "[.[] | {login: .author.login, message: .commit.message}] | tojson",
    )
    rows = []
    try:
        for line in raw.split("\n"):
            if line.strip():
                rows.extend(json.loads(line))
        logins = []
        for row in rows:
            logins += [row["login"], *_NOREPLY_TRAILER.findall(row["message"] or "")]
    except (ValueError, TypeError, KeyError):
        raise LookupFailed("the commit list wasn't the JSON the check expects", permanent=True) from None
    if len(rows) >= _COMMIT_CAP:
        raise LookupFailed(
            f"GitHub lists at most {_COMMIT_CAP} commits of a PR, so the authors of any beyond that can't be read",
            True,
        )
    return [{"login": login} for login in logins if not (isinstance(login, str) and login.endswith("[bot]"))]


def credited_authors(pr_author, commit_authors, text):
    """The login of each commit author, other than the PR's, `text` doesn't credit.

    A credit counts only in the message's last paragraph, and only when every
    line of it is a trailer, as git reads them. An author with no login gets
    no line, as git.md says. Logins compare without regard to case, as
    GitHub's do.
    """
    last = re.split(r"\n[ \t]*\n", text.strip())[-1]
    trailers = last if all(_TRAILER_LINE.fullmatch(line) for line in last.splitlines()) else ""
    seen = {pr_author.lower()}
    missing = []
    for author in commit_authors:
        login = author.get("login")
        if not login or login.lower() in seen:
            continue
        seen.add(login.lower())
        trailer = rf"^Co-authored-by:.*<\d+\+{re.escape(login)}@users\.noreply\.github\.com>[ \t]*$"
        if not re.search(trailer, trailers, re.IGNORECASE | re.MULTILINE):
            missing.append(login)
    return missing


def credit_reason(lines, doc, id_failure=""):
    """A refusal naming each credit line the squash message needs."""
    listed = "\n".join(f"- {line}" for line in lines)
    reason = (
        f"The squash message lacks credit for commit authors other than the PR's. "
        f"Add, as the message's last paragraph, after a blank line below any `Closes` lines:\n{listed}\n"
        f"The name before the address is free. See the Squash credit rule in {doc}."
    )
    if "<id>" in listed:
        reason += (
            f" `<id>` is a placeholder: the id lookup failed ({id_failure}), so replace it with the author's "
            "numeric GitHub id, from `gh api users/<login> -q .id`. A line left as `<id>` is refused again."
        )
    return reason


def lookup_reason(error, doc):
    """A refusal for a merge whose PR authors couldn't be read, so its credit lines can't be checked."""
    if error.permanent:
        return (
            f"Couldn't read all of the PR's commit authors, so the squash credit lines can't be checked: {error}. "
            "No retry of this command will pass. Ask the reviewer to merge it in GitHub's UI, which adds "
            f"these trailers itself (ADR 074). See {doc}."
        )
    return (
        f"Couldn't read the PR's authors, so the squash credit lines can't be checked: {error}. "
        "A squash commit can't be amended once merged. Fix that, then retry the same merge "
        f"(nothing was pushed, so an approval of the head stands). See {doc}."
    )


def unreadable_reason(detail, doc):
    """A refusal for a merge whose body, or directory, the hook can't read."""
    return (
        f"Couldn't read this `gh pr merge`: {detail}. The hook can't check what it can't read, and a squash "
        "commit can't be amended once merged. Give the body with `--body-file -` and a quoted heredoc "
        f"(`<<'EOF'`), as the merge skill does. See {doc}."
    )


def crash_reason():
    """A refusal for a merge the check itself crashed on."""
    return (
        "The merge-message hook failed on this `gh pr merge`, so the squash message can't be checked, and a "
        "squash commit can't be amended once merged. Retry the merge; if it fails again, "
        "hooks/pretooluse-merge-message.py needs fixing."
    )


def gh(cwd, deadline, *args):
    """Run a `gh` command and return stdout. Raises LookupFailed if it fails or runs out of time.

    The lookup gets _GH_TIMEOUT seconds, or what is left before `deadline` (a
    time.monotonic() value) if that is less.
    """
    label = "`gh " + " ".join(args[:2] if args[0] == "pr" else args[:1]) + "`"
    left = min(_GH_TIMEOUT, deadline - time.monotonic())
    if left <= 0:
        raise LookupFailed(f"{label} had no time left")
    env = {key: value for key, value in os.environ.items() if key not in _COLOUR_VARS}
    env.update(NO_COLOR="1", GH_PROMPT_DISABLED="1")
    try:
        done = subprocess.run(
            ("gh", *args), cwd=cwd, capture_output=True, text=True, check=False, timeout=left, env=env
        )
    except subprocess.TimeoutExpired:
        raise LookupFailed(f"{label} timed out") from None
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise LookupFailed(f"{label} couldn't run ({type(error).__name__}); is `gh` installed?") from None
    if done.returncode != 0:
        lines = done.stderr.strip().splitlines()
        reason = re.sub(r"[^\x20-\x7e]", "?", lines[0])[:200] if lines else f"exit status {done.returncode}"
        raise LookupFailed(f"{label} failed: {reason}")
    return done.stdout


def deny(reason):
    """Refuse the tool call through PreToolUse's documented JSON decision."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
