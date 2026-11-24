#!/usr/bin/env python3
"""The kit's git naming rules, as code - one copy every check imports.

Mirror of conventions/git.md's Branches and Commits rules - change both
together. See ADR 046 (branches) and ADR 047 (commit messages) under
docs/decisions/.

Imported by the PreToolUse hooks and the `commit-msg` git hook, which sit next
to it in hooks/. Run directly, it checks one thing and exits 1 with the
reasons when it breaks a rule:

    conventions.py branch <name>
    conventions.py pr-title <title> <pr-number> [<body-file> | -]
    conventions.py message <file>

Standard library only - the hooks run in whatever repo the session or commit
is in, so this must not depend on that repo's toolchain.
"""

import os
import re
import shlex
import subprocess
import sys

BRANCH_PREFIXES = ("feature/", "bugfix/", "hotfix/", "release/", "chore/")
BRANCH_MAX = 50
COMMIT_TYPES = ("feat", "fix", "docs", "refactor", "test", "chore")
SUBJECT_MAX = 72
BODY_MAX = 72

KIT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# `!` after the type marks a breaking change, and always comes with a footer
# saying what to do; the spec allows either spelling of it.
SUBJECT = re.compile(r"(?P<type>[a-z]+)(?P<bang>!)?: (?P<description>.+)")
BREAKING_FOOTER = re.compile(r"^BREAKING[ -]CHANGE: \S", re.MULTILINE)
# A body line allowed past BODY_MAX: one unbreakable word - a URL or a path -
# optionally after a list marker or a `[1]: ` link label, since wrapping it is
# impossible.
UNWRAPPABLE = re.compile(r"\s*(?:[-*]\s+|\d+\.\s+|\[[^\]]+\]:\s+)?\S+")
# A `Co-authored-by:` trailer is allowed past BODY_MAX too: git.md requires it,
# and a name, a login and a nine-digit id can't be wrapped to fit.
CREDIT_LINE = re.compile(r"Co-authored-by: .+ <[^<>\s]+>\s*", re.IGNORECASE)
# Messages git writes itself, not the committer.
GENERATED = ("Merge ", 'Revert "', "fixup! ", "squash! ", "amend! ")
SCISSORS = "# ------------------------ >8 ------------------------"

SEPARATORS = {"&&", "||", ";", "|", "&", "\n", "(", ")", "|&", ";;"}


def branch_problem(name):
    """Why a branch name breaks the rules, or None when it doesn't."""
    if not name.startswith(BRANCH_PREFIXES) or name in BRANCH_PREFIXES:
        return "has no allowed prefix"
    if len(name) > BRANCH_MAX:
        return f"is {len(name)} characters, over the {BRANCH_MAX}-character limit"
    return None


def branch_reason(name, problem, doc):
    """A refusal naming what's wrong with a branch name and the rules in full."""
    allowed = ", ".join(f"`{prefix}`" for prefix in BRANCH_PREFIXES)
    return (
        f"Branch name `{name}` {problem}. The convention is "
        f"`type/short-description`, lowercase and hyphen-separated, with the "
        f"prefix one of {allowed}, at most {BRANCH_MAX} characters in all. "
        f"Pick a conforming name and retry - see {doc}."
    )


def subject_problems(subject, pr=None):
    """What's wrong with a commit subject.

    With `pr`, the subject is a squash commit's and must end ` (#pr)`; pass
    "any" when the number isn't known, to require some ` (#N)`.
    """
    problems = []
    if len(subject) > SUBJECT_MAX:
        problems.append(f"is {len(subject)} characters, over the {SUBJECT_MAX}-character limit")
    if pr is not None:
        suffix = r" \(#\d+\)" if pr == "any" else re.escape(f" (#{pr})")
        if not re.search(suffix + "$", subject):
            wanted = "(#N)" if pr == "any" else f"(#{pr})"
            problems.append(f"doesn't end with the PR number, ` {wanted}`")
        subject = re.sub(r" \(#\d+\)$", "", subject)
    return problems + title_problems(subject)


def title_problems(title):
    """What's wrong with a subject's `type: description`, length aside."""
    problems = []
    match = SUBJECT.fullmatch(title)
    if not match:
        problems.append("isn't `type: description`")
    else:
        if match["type"] not in COMMIT_TYPES:
            problems.append(f"has type `{match['type']}`, not one of {', '.join(COMMIT_TYPES)}")
        if match["description"][:1].isupper():
            problems.append("starts its description with a capital")
    if title.endswith("."):
        problems.append("ends with a period")
    return problems


def breaking_problems(subject, body, where="the body"):
    """What's wrong with how a breaking change is marked: `!` and footer go together."""
    match = SUBJECT.fullmatch(re.sub(r" \(#\d+\)$", "", subject))
    bang = bool(match and match["bang"])
    footer = bool(BREAKING_FOOTER.search(body))
    if bang and not footer:
        return [f"marks a breaking change with `!`, but {where} has no `BREAKING CHANGE:` line saying what to do"]
    if footer and not bang:
        return [f"has a `BREAKING CHANGE:` line in {where}, but no `!` after the type"]
    return []


def pr_title_problems(title, pr, body=None):
    """What's wrong with a PR title, which becomes the squash subject plus ` (#pr)`.

    With `body`, the PR's description is checked for the breaking-change
    footer a `!` title needs, and the reverse.
    """
    limit = SUBJECT_MAX - len(f" (#{pr})")
    problems = []
    if len(title) > limit:
        problems.append(
            f"is {len(title)} characters, over {limit} - the subject limit of "
            f"{SUBJECT_MAX} once GitHub appends ` (#{pr})`"
        )
    problems += title_problems(title)
    if body is not None:
        problems += breaking_problems(title, body, "the PR body")
    return problems


def title_reason(title, problems, doc):
    """A refusal listing a PR title's problems and the rules in full."""
    listed = "\n".join(f"- {problem}" for problem in problems)
    return (
        f"PR title `{title}` breaks the convention:\n{listed}\n"
        f"A PR title becomes the squash commit's subject, so it is `type: description` "
        f"(`type!:` for a breaking change) - "
        f"type one of {', '.join(COMMIT_TYPES)}, description lowercase, no trailing "
        f"period - within {SUBJECT_MAX} characters once ` (#N)` is appended. A `!` title "
        f"needs a `BREAKING CHANGE:` line in the PR body, and that line needs `!`. See {doc}."
    )


def message_problems(message, pr=None):
    """What's wrong with a whole commit message; see subject_problems for `pr`.

    Without `pr` the message is one git is committing, so its `#` lines are
    dropped as git drops them, and a message git wrote itself passes. A squash
    message is passed to gh verbatim, and neither applies.
    """
    if pr is None:
        message = strip_comments(message)
    lines = message.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ["is empty"]
    if pr is None and lines[0].startswith(GENERATED):
        return []
    problems = [f"subject {problem}" for problem in subject_problems(lines[0], pr)]
    problems += breaking_problems(lines[0], "\n".join(lines[1:]))
    if len(lines) > 1 and lines[1].strip():
        problems.append("has no blank line after the subject")
    for number, line in enumerate(lines[1:], start=2):
        if len(line) > BODY_MAX and not (UNWRAPPABLE.fullmatch(line) or CREDIT_LINE.fullmatch(line)):
            problems.append(f"line {number} is {len(line)} characters, over the {BODY_MAX}-character wrap")
    return problems


def strip_comments(message):
    """The message as git will store it: no `#` lines, nothing past the scissors."""
    message = message.split(SCISSORS, 1)[0]
    return "\n".join(line for line in message.splitlines() if not line.startswith("#"))


def message_reason(problems, doc):
    """A refusal listing a message's problems and the rules in full."""
    listed = "\n".join(f"- {problem}" for problem in problems)
    return (
        f"Commit message breaks the convention:\n{listed}\n"
        f"The subject is `type: description` (`type!:` for a breaking change) - "
        f"type one of {', '.join(COMMIT_TYPES)}, "
        f"description lowercase, no trailing period - at most {SUBJECT_MAX} characters, "
        f"then a blank line and a body wrapped at {BODY_MAX}, with a `BREAKING CHANGE:` "
        f"line whenever the subject has `!`. See {doc}."
    )


# `<<WORD`, not the here-string `<<<WORD`. The delimiter is a quoted word (the
# quote is group 2, the word group 3) or a bare one (a backslash before it is
# group 4, the word group 5, which starts with a letter or `_`, so `1<<20` and
# `<<%s` are not heredocs); quoting any part of it stops the shell expanding
# the body.
HEREDOC = re.compile(
    r"(?<!<)<<(?!<)(-?)\s*(?:(['\"])([^'\"\n]+)\2|(\\)?([A-Za-z_][^\s'\"\\<>|&;()$`]*))"
)


def scan_heredocs(command):
    """The command with each heredoc's body cut out, and a (body, quoted, delimiter) for each, in order.

    A body is text, not shell: an apostrophe in it would otherwise read as an
    unclosed quote and make the whole command unparseable. `quoted` is whether
    the delimiter was quoted, which stops the shell expanding the body. A
    `<<WORD` that no later line closes is no heredoc: its line is kept as
    shell, and the lines after it are scanned afresh.
    """
    lines = command.split("\n")
    ignore = set()
    while True:
        kept, found, unclosed = scan_lines(lines, ignore)
        if unclosed is None:
            return "\n".join(kept), found
        ignore.add(unclosed)


def scan_lines(lines, ignore):
    """The (kept lines, heredocs, line of the first unclosed `<<` or None) of one pass of `scan_heredocs`."""
    found = []
    kept = []
    pending = []
    for number, line in enumerate(lines):
        if pending:
            strip_tabs, delimiter, quoted, body, _ = pending[0]
            text = line.lstrip("\t") if strip_tabs else line
            if text == delimiter:
                found.append(("\n".join(body), quoted, delimiter))
                pending.pop(0)
            else:
                body.append(text)
            continue
        kept.append(line)
        if number not in ignore:
            pending = [
                (dash == "-", qword or plain, bool(quote or backslash), [], number)
                for dash, quote, qword, backslash, plain in HEREDOC.findall(line)
            ]
    return kept, found, (pending[0][4] if pending else None)


def segments(command):
    """Split a shell command into the word lists of its simple commands."""
    parsed, _, _, _ = parse_command(command)
    for words, _, _ in parsed:
        yield words


def parse_command(command):
    """Split a shell command into its simple commands and the heredocs it opens.

    Returns (segments, heredocs, matched, complete). Each segment is (words,
    heredoc numbers, nested): `nested` is whether it runs in a subshell, inside
    parentheses or backgrounded or in a pipeline, where a `cd` doesn't outlast
    it. A comment is dropped, its newline kept. The heredoc
    numbers are the position, in `heredocs`, of each heredoc the simple command
    opens, whether with a `<<` of its own or inside a quoted word such as
    `"$(cat <<'EOF' ...)"`. `heredocs` is `scan_heredocs`'s list. `matched` is
    false when the delimiters the lexer saw after its `<<` operators differ
    from the ones the scan found (an arithmetic `<<`, a `<<` in a comment, a
    delimiter the scan doesn't read), in which case the numbers can't be
    trusted. `complete` is false when the lexer gave up on the command (an
    unbalanced quote), so the simple command it was in the middle of is lost.
    A backslash-newline joins the lines, and a backslash that ends the
    command is dropped, as the shell does.
    """
    command, found = scan_heredocs(command)
    command = drop_shell_comments(command)
    command = re.sub(r"(?<!\\)((?:\\\\)*)\\\n", r"\1", command)
    command = re.sub(r"(?<!\\)((?:\\\\)*)\\\Z", r"\1", command)
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
    lexer.commenters = ""
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    parsed = []
    words = []
    numbers = []
    delimiters = []
    redirect = False
    depth = 0
    piped = False
    complete = True
    try:
        for token in lexer:
            if token in SEPARATORS:
                # A command in parentheses, backgrounded or in a pipeline runs in a subshell.
                forked = token in ("&", "|", "|&")
                parsed.append((words, numbers, depth > 0 or piped or forked))
                words, numbers, redirect = [], [], False
                depth = max(0, depth + (token == "(") - (token == ")"))
                piped = token in ("|", "|&")
            elif re.fullmatch(r"[<>&|]+", token):
                # A redirection: drop its fd (`2>`) and, next pass, its target.
                if words and words[-1].isdigit():
                    words.pop()
                if token == "<<":
                    numbers.append(len(delimiters))
                    delimiters.append(None)
                redirect = True
            elif redirect:
                if delimiters and delimiters[-1] is None:
                    delimiters[-1] = token.lstrip("-")
                redirect = False
            else:
                words.append(token)
                for match in HEREDOC.findall(token):
                    numbers.append(len(delimiters))
                    delimiters.append(match[2] or match[4])
        parsed.append((words, numbers, depth > 0 or piped))
    except ValueError:
        complete = False
    return parsed, found, delimiters == [delimiter for _, _, delimiter in found], complete


def drop_shell_comments(command):
    """The command with each comment cut out and its newline kept.

    A comment starts at an unquoted `#` that begins a word. shlex's own comment
    handling would swallow the newline too, joining the next line's words to
    this one's.
    """
    out = []
    quote = None
    index = 0
    while index < len(command):
        char = command[index]
        if quote:
            out.append(char)
            if char == "\\" and quote != "'" and index + 1 < len(command):
                index += 1
                out.append(command[index])
            elif char == quote:
                quote = None
        elif char == "\\" and index + 1 < len(command):
            out.append(command[index : index + 2])
            index += 1
        elif char in "'\"":
            quote = char
            out.append(char)
        elif char == "#" and (index == 0 or command[index - 1] in " \t\n;&|()"):
            while index + 1 < len(command) and command[index + 1] != "\n":
                index += 1
        else:
            out.append(char)
        index += 1
    return "".join(out)


def reaches_kit(directory):
    """git.md's path as the repo at `directory` reaches it, or None if it doesn't.

    A linked worktree lacks the gitignored `.fieldkit` symlink, so the main
    worktree - the common git dir's parent - is checked as well.
    """
    return kit_status(directory)[0]


def kit_status(directory):
    """(git.md's path or None, why git couldn't say or None) for the repo at `directory`.

    The second is set when `reaches_kit` would read a kit repo as no kit repo:
    git is missing, runs past GIT_TIMEOUT seconds or refuses the directory
    (safe.directory). A directory that is no repo at all is an answer, not
    trouble.
    """
    roots = set()
    top, trouble = git_output(directory, "rev-parse", "--show-toplevel")
    if trouble:
        return None, trouble
    if top:
        roots.add(os.path.realpath(top.strip()))
        common, trouble = git_output(directory, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if trouble:
            return None, trouble
        if common:
            roots.add(os.path.dirname(os.path.realpath(common.strip())))
    for root in roots:
        if root == KIT:
            return "conventions/git.md", None
        if os.path.exists(os.path.join(root, ".fieldkit")):
            return ".fieldkit/conventions/git.md", None
    return None, None


GIT_TIMEOUT = 10


def git_output(cwd, *args):
    """(stdout or None, trouble or None) of a git command.

    Run in the C locale so "not a git repository" can be told from a refusal.
    Output is read leniently: a path that isn't UTF-8 must not crash the hook.
    """
    try:
        done = subprocess.run(
            ("git", *args),
            cwd=cwd,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=GIT_TIMEOUT,
            env={**os.environ, "LC_ALL": "C", "LANGUAGE": "C"},
        )
    except subprocess.TimeoutExpired:
        return None, f"git ran past {GIT_TIMEOUT} seconds"
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"git can't be run ({error})"
    if done.returncode == 0:
        return done.stdout, None
    if "not a git repository" in done.stderr:
        return None, None
    return None, f"git refused the directory: {done.stderr.strip() or 'exit ' + str(done.returncode)}"


def git(cwd, *args):
    """Run a git command, returning stdout, or None if it failed or ran past GIT_TIMEOUT seconds."""
    return git_output(cwd, *args)[0]


def main():
    doc = "conventions/git.md"
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "branch":
        problem = branch_problem(args[1])
        if problem:
            sys.exit(branch_reason(args[1], problem, doc))
    elif len(args) in (3, 4) and args[0] == "pr-title":
        body = None
        if len(args) == 4:
            with open(0 if args[3] == "-" else args[3], encoding="utf-8") as handle:
                body = handle.read()
        problems = pr_title_problems(args[1], args[2], body)
        if problems:
            sys.exit(title_reason(args[1], problems, doc))
    elif len(args) == 2 and args[0] == "message":
        with open(args[1], encoding="utf-8") as handle:
            problems = message_problems(handle.read())
        if problems:
            sys.exit(message_reason(problems, doc))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
