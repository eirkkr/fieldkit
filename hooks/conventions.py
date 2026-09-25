#!/usr/bin/env python3
"""The kit's git naming rules, as code - one copy every check imports.

Mirror of conventions/git.md's Branches and Commits rules - change both
together. See ADR 046 (branches) and ADR 047 (commit messages) under
docs/decisions/.

Imported by the PreToolUse hooks and the `commit-msg` git hook, which sit next
to it in hooks/. Run directly, it checks one thing and exits 1 with the
reasons when it breaks a rule:

    conventions.py branch <name>
    conventions.py pr-title <title> <pr-number>
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

SUBJECT = re.compile(r"(?P<type>[a-z]+): (?P<description>.+)")
# A body line allowed past BODY_MAX: one unbreakable word - a URL or a path -
# optionally after a list marker or a `[1]: ` link label, since wrapping it is
# impossible.
UNWRAPPABLE = re.compile(r"\s*(?:[-*]\s+|\d+\.\s+|\[[^\]]+\]:\s+)?\S+")
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


def pr_title_problems(title, pr):
    """What's wrong with a PR title, which becomes the squash subject plus ` (#pr)`."""
    limit = SUBJECT_MAX - len(f" (#{pr})")
    problems = []
    if len(title) > limit:
        problems.append(
            f"is {len(title)} characters, over {limit} - the subject limit of "
            f"{SUBJECT_MAX} once GitHub appends ` (#{pr})`"
        )
    return problems + title_problems(title)


def title_reason(title, problems, doc):
    """A refusal listing a PR title's problems and the rules in full."""
    listed = "\n".join(f"- {problem}" for problem in problems)
    return (
        f"PR title `{title}` breaks the convention:\n{listed}\n"
        f"A PR title becomes the squash commit's subject, so it is `type: description` - "
        f"type one of {', '.join(COMMIT_TYPES)}, description lowercase, no trailing "
        f"period - within {SUBJECT_MAX} characters once ` (#N)` is appended. See {doc}."
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
    if len(lines) > 1 and lines[1].strip():
        problems.append("has no blank line after the subject")
    for number, line in enumerate(lines[1:], start=2):
        if len(line) > BODY_MAX and not UNWRAPPABLE.fullmatch(line):
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
        f"The subject is `type: description` - type one of {', '.join(COMMIT_TYPES)}, "
        f"description lowercase, no trailing period - at most {SUBJECT_MAX} characters, "
        f"then a blank line and a body wrapped at {BODY_MAX}. See {doc}."
    )


HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")


def heredocs(command):
    """The command with each heredoc's body cut out, and the bodies in order.

    A body is text, not shell: an apostrophe in it would otherwise read as an
    unclosed quote and make the whole command unparseable.
    """
    bodies = []
    kept = []
    lines = command.split("\n")
    pending = []
    for line in lines:
        if pending:
            strip_tabs, delimiter, body = pending[0]
            if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                bodies.append("\n".join(body))
                pending.pop(0)
            else:
                body.append(line)
            continue
        kept.append(line)
        pending = [(dash == "-", word, []) for dash, _, word in HEREDOC.findall(line)]
    return "\n".join(kept), bodies


def segments(command):
    """Split a shell command into the word lists of its simple commands."""
    command, _ = heredocs(command)
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();<>|&\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    words = []
    redirect = False
    try:
        for token in lexer:
            if token in SEPARATORS:
                yield words
                words, redirect = [], False
            elif re.fullmatch(r"[<>&|]+", token):
                # A redirection: drop its fd (`2>`) and, next pass, its target.
                if words and words[-1].isdigit():
                    words.pop()
                redirect = True
            elif redirect:
                redirect = False
            else:
                words.append(token)
    except ValueError:
        return
    yield words


def reaches_kit(directory):
    """git.md's path as the repo at `directory` reaches it, or None if it doesn't.

    A linked worktree lacks the gitignored `.fieldkit` symlink, so the main
    worktree - the common git dir's parent - is checked as well.
    """
    roots = set()
    top = git(directory, "rev-parse", "--show-toplevel")
    if top:
        roots.add(os.path.realpath(top.strip()))
    common = git(directory, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common:
        roots.add(os.path.dirname(os.path.realpath(common.strip())))
    for root in roots:
        if root == KIT:
            return "conventions/git.md"
        if os.path.exists(os.path.join(root, ".fieldkit")):
            return ".fieldkit/conventions/git.md"
    return None


def git(cwd, *args):
    """Run a git command, returning stdout, or None if it failed."""
    try:
        done = subprocess.run(
            ("git", *args), cwd=cwd, capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def main():
    doc = "conventions/git.md"
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == "branch":
        problem = branch_problem(args[1])
        if problem:
            sys.exit(branch_reason(args[1], problem, doc))
    elif len(args) == 3 and args[0] == "pr-title":
        problems = pr_title_problems(args[1], args[2])
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
