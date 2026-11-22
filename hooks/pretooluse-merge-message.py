#!/usr/bin/env python3
"""PreToolUse hook: refuse a squash merge whose commit message breaks the kit's rules.

The kit squash-merges, so the only commit a PR leaves on the default branch is
the one `gh pr merge --subject ... --body ...` writes. This hook checks that
message before the merge runs: the subject's type, case, length and ` (#N)`
suffix, and the body's wrapping - the rules in conventions.py, next to this
file.

The body is read from `--body`/`-b`, or from `--body-file`/`-F` naming a file
or `-` fed by a heredoc (a `--body "$(cat <<'EOF' ...)"` counts as one). With
no `--subject`, GitHub builds the subject from the PR title, which CI checks
instead. The PR number comes from a numeric or URL argument; otherwise any
` (#N)` is accepted.

It also refuses a message lacking the `Co-authored-by` line for each commit
author who isn't the PR's author (git.md's Squash credit rule), whenever the
command gives a subject or a body. That needs the PR's authors, so it asks
`gh pr view` - the one network call a merge pays - and, for a PR of 100
commits or more, pages through the REST commit list. A refusal makes one more
call, `gh api users/<login>`, per missing author, to spell out the line.

In a repo that reaches the kit, a `gh pr merge` the hook can't check is
refused, not let through: a squash commit can't be amended, so an unchecked
merge is the worse outcome (ADR 074). That covers a lookup that fails, times
out or is unreadable, a subject or body the shell rewrites or a file that
can't be read, and an error in the check itself. `FOO=1`, `env` or `command`
before `gh`, and `-R`/`--repo` between `gh` and `pr`, are read; a merge run
through `bash -c`, `eval`, `xargs` or `gh api` is not recognised.

Like the branch-name hook it applies only in a repo that reaches the kit and
refuses through PreToolUse's JSON `deny`. See ADR 047 under docs/decisions/.

Registered in ~/.claude/settings.json by `just install`
(scripts/register-hooks.sh); not meant to be invoked directly. Standard
library only.
"""

import json
import os
import re
import subprocess
import sys
import time

from conventions import heredocs, message_problems, message_reason, reaches_kit, segments

# Every `gh pr merge` flag that takes a value, so a value is never read as the PR.
# A short flag's value may follow it, or follow `=`, or be joined to it (`-bTEXT`).
_LONG_VALUE_FLAGS = frozenset(
    {"--subject", "--body", "--body-file", "--repo", "--match-head-commit", "--author-email"}
)
_SHORT_VALUE_FLAGS = {"t": "--subject", "b": "--body", "F": "--body-file", "R": "--repo", "A": "--author-email"}

# `FOO=1` ahead of a command.
_ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*")

# A `$name`, `${...}`, `$(...)` or backtick: the shell rewrites the value first.
_EXPANSION = re.compile(r"\$[({A-Za-z_]|`")
# `$(cat <<'EOF'` with its body cut out of the command: the usual way to pass a body.
_CAT_HEREDOC = re.compile(r"\$\(\s*cat\s+<<-?\s*['\"]?\w+['\"]?\s*\)")

# A trailer line is `Token: value` or an indented continuation. Git reads
# trailers only in a last paragraph made of them.
_TRAILER_LINE = re.compile(r"[A-Za-z][A-Za-z0-9-]*:[ \t]+\S.*|[ \t]+\S.*")

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


class Unreadable(Exception):
    """A `gh pr merge` whose subject or body the hook can't read."""


class LookupFailed(Exception):
    """The PR's authors couldn't be read; the message says why."""


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or "merge" not in command:
        return

    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    _, bodies = heredocs(command)
    for words in segments(command):
        if words[:1] == ["cd"] and len(words) == 2:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        found = merge_arguments(words)
        if found is None:
            continue
        try:
            reason = check_merge(*found, bodies, cwd)
        except Exception:  # noqa: BLE001 - registered `|| true`, so a crash would let the merge through
            reason = crash_reason()
        if reason:
            deny(reason)
            return


def merge_arguments(words):
    """The (arguments after `pr merge`, repo named before `pr`) of a `gh pr merge`, or None.

    `FOO=1`, `env` and `command` may come first, and `gh`'s own `-R`/`--repo`
    may sit between `gh` and `pr`, where it names the repo like the flag after.
    """
    index = 0
    while index < len(words) and (_ASSIGNMENT.fullmatch(words[index]) or words[index] in ("command", "env")):
        index += 1
    if words[index : index + 1] != ["gh"]:
        return None
    index += 1
    repo = None
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
    if words[index : index + 2] != ["pr", "merge"]:
        return None
    return words[index + 2 :], repo


def check_merge(args, repo, bodies, cwd):
    """The refusal for one `gh pr merge`'s arguments, or None to let it through."""
    try:
        message = merge_message(args, repo, bodies, cwd)
    except Unreadable as error:
        doc = reaches_kit(cwd)
        return unreadable_reason(str(error), doc) if doc else None
    if message is None:
        return None
    doc = reaches_kit(cwd)
    if not doc:
        return None
    pr, subject, text, selector, repo = message
    reasons = []
    if subject is not None:
        problems = message_problems(text, pr)
        if problems:
            reasons.append(message_reason(problems, doc))
    try:
        missing = missing_credit_lines(text, selector, repo, cwd)
    except LookupFailed as error:
        reasons.append(lookup_reason(str(error), doc))
    else:
        if missing:
            reasons.append(credit_reason(missing, doc))
    return "\n\n".join(reasons) or None


def merge_message(args, repo, bodies, cwd):
    """The (PR number or "any", subject, text, PR selector, repo) a `gh pr merge` would write, or None.

    `subject` is the subject to lint, None where the command gives none or the
    shell rewrites it; `text` is the whole message, the part the credit check
    reads. The selector is None where the command names none, and `repo` is
    the one passed in unless a flag names another. None overall when the
    command gives neither subject nor body - GitHub then builds the message,
    and CI checks the PR title - or when a flag has no value, which `gh`
    refuses itself. Raises Unreadable for a body the hook
    can't read.
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
            body = read_body(value, bodies)
        elif flag == "--repo":
            repo = value
        elif flag == "--body-file":
            body = read_body_file(value, bodies, cwd)
    if subject is None and body is None:
        return None
    text = subject if body is None else (body if subject is None else subject + ("\n\n" + body if body else ""))
    return pr, None if subject is None or _EXPANSION.search(subject) else subject, text, selector, repo


def short_flag(arg):
    """The (long flag, joined value or None) of a short-flag cluster such as `-sbTEXT`, else (None, None).

    The boolean flags (`-s`, `-m`, `-r`, `-d`) can be bundled before a
    value-taking one; whatever follows that one is its value, as in `gh`'s own
    parser, with a leading `=` dropped.
    """
    for position, letter in enumerate(arg[1:], start=1):
        flag = _SHORT_VALUE_FLAGS.get(letter)
        if flag:
            rest = arg[position + 1 :]
            return flag, (rest[1:] if rest.startswith("=") else rest) or None
    return None, None


def read_body(value, bodies):
    """A `--body`'s text, taking a `$(cat <<'EOF' ...)` from the command's heredoc."""
    if _CAT_HEREDOC.fullmatch(value):
        if len(bodies) == 1:
            return bodies[0]
        raise Unreadable("`--body` takes its text from a heredoc, but the command has more than one")
    if _EXPANSION.search(value):
        raise Unreadable("`--body` holds a shell expansion")
    return value


def read_body_file(path, bodies, cwd):
    """A `--body-file`'s text - the command's heredoc for `-` - or raise Unreadable."""
    if path == "-":
        if len(bodies) == 1:
            return bodies[0]
        raise Unreadable("`--body-file -` needs exactly one heredoc in the command to read")
    try:
        with open(os.path.join(cwd, path), encoding="utf-8") as handle:
            return handle.read()
    except (OSError, ValueError):
        raise Unreadable(f"`--body-file {path}` can't be read as UTF-8 text") from None


def missing_credit_lines(text, selector, repo, cwd):
    """The `Co-authored-by` lines `text` lacks ([] when none). Raises LookupFailed when the PR can't be read."""
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
        commit_authors = paged_commit_authors(cwd, deadline, url)
    if not isinstance(author, str) or not author:
        raise LookupFailed("the PR has no author login")
    if not all(isinstance(a, dict) and isinstance(a.get("login") or "", str) for a in commit_authors):
        raise LookupFailed("a commit author wasn't the shape the check expects")
    lines = []
    for login, name in credited_authors(author, commit_authors, text):
        try:
            found = gh(cwd, deadline, "api", f"users/{login}", "-q", ".id").strip()
        except LookupFailed:
            found = ""
        user_id = found if found.isdigit() else "<id>"
        lines.append(f"Co-authored-by: {name} <{user_id}+{login}@users.noreply.github.com>")
    return lines


def paged_commit_authors(cwd, deadline, url):
    """Every commit author of a PR with at least a page of commits, from the REST list."""
    match = re.fullmatch(r"https://([^/]+)/([^/]+)/([^/]+)/pull/(\d+)", url) if isinstance(url, str) else None
    if not match:
        raise LookupFailed("a PR of 100 commits or more needs its URL, to page through the rest")
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
        "[.[] | {login: .author.login, name: .commit.author.name}] | tojson",
    )
    authors = []
    try:
        for line in raw.splitlines():
            if line.strip():
                authors.extend(json.loads(line))
    except (ValueError, TypeError):
        raise LookupFailed("the commit list wasn't the JSON the check expects") from None
    if len(authors) >= _COMMIT_CAP:
        raise LookupFailed(f"GitHub lists at most {_COMMIT_CAP} commits of a PR, so the authors of the rest can't be read")
    return authors


def credited_authors(pr_author, commit_authors, text):
    """The (login, name) of each commit author, other than the PR's, `text` doesn't credit.

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
            missing.append((login, plain_name(author.get("name"), login)))
    return missing


def plain_name(name, login):
    """A commit author's name as fit for a refusal's credit line, or the login.

    The name is git metadata anyone can set, and it ends up in text the agent
    acts on, so only letters, digits, spaces and `.'-` stay, up to 60.
    """
    cleaned = re.sub(r"[^\w .'-]", "", name if isinstance(name, str) else "").strip()[:60].strip()
    return cleaned or login


def credit_reason(lines, doc):
    """A refusal naming each credit line the squash message needs."""
    listed = "\n".join(f"- {line}" for line in lines)
    reason = (
        f"The squash message lacks credit for commit authors other than the PR's. "
        f"Add, as the message's last paragraph, after a blank line below any `Closes` lines:\n{listed}\n"
        f"See the Squash credit rule in {doc}."
    )
    if "<id>" in listed:
        reason += (
            " `<id>` is a placeholder: the id lookup failed, so replace it with the author's "
            "numeric GitHub id, from `gh api users/<login> -q .id`. A line left as `<id>` is refused again."
        )
    return reason


def lookup_reason(detail, doc):
    """A refusal for a merge whose PR authors couldn't be read, so its credit lines can't be checked."""
    return (
        f"Couldn't read the PR's authors, so the squash credit lines can't be checked: {detail}. "
        "A squash commit can't be amended once merged. Fix that, then retry the same merge "
        f"(nothing was pushed, so an approval of the head stands). See {doc}."
    )


def unreadable_reason(detail, doc):
    """A refusal for a merge whose message the hook can't read."""
    return (
        f"Couldn't read the message of this `gh pr merge`: {detail}. The shell rewrites a value holding `$` "
        "or a backtick before `gh` sees it, so the hook can't check the squash message, and a squash commit "
        "can't be amended once merged. Pass the body with `--body-file -` and a quoted heredoc (`<<'EOF'`), "
        f"and the subject without shell expansions. See {doc}."
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
