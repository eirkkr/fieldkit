#!/usr/bin/env python3
"""PreToolUse hook: refuse a squash merge whose commit message breaks the kit's rules.

The kit squash-merges, so the only commit a PR leaves on the default branch is
the one `gh pr merge --subject ... --body ...` writes. This hook checks that
message before the merge runs: the subject's type, case, length and ` (#N)`
suffix, and the body's wrapping - the rules in conventions.py, next to this
file.

The body is read from `--body`/`-b`, or from `--body-file`/`-F` naming a file
or `-` fed by a heredoc. With no `--subject`, GitHub builds the subject from
the PR title, which CI checks instead. The PR number comes from the command's
argument; with none, any ` (#N)` is accepted.

It also refuses a message lacking the `Co-authored-by` line for each commit
author who isn't the PR's author (git.md's Squash credit rule), whenever the
command gives a subject or a body. That needs the PR's authors, so it asks
`gh pr view` - the one network call a merge pays, and a second,
`gh api users/<login>`, only to word a refusal. A lookup that fails, times out
or is unreadable, or an error in the check itself, refuses the merge: a squash
commit can't be amended, so an unchecked merge is the worse outcome (ADR 074).

Like the branch-name hook it applies only in a repo that reaches the kit, lets
through a command it can't parse, and refuses through PreToolUse's JSON `deny`.
See ADR 047 under docs/decisions/.

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
VALUE_FLAGS = {
    "--subject",
    "-t",
    "--body",
    "-b",
    "--body-file",
    "-F",
    "--repo",
    "-R",
    "--match-head-commit",
    "--author-email",
    "-A",
}

# Seconds one `gh` lookup may take, and all of a merge's lookups together: past
# either the lookup counts as failed and the merge is refused.
GH_TIMEOUT = 15
GH_TOTAL = 25


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or "merge" not in command:
        return

    cwd = payload.get("cwd") or os.getcwd()
    _, bodies = heredocs(command)
    for words in segments(command):
        if words[:1] == ["cd"] and len(words) == 2:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        if words[:3] != ["gh", "pr", "merge"]:
            continue
        message = merge_message(words[3:], bodies, cwd)
        if message is None:
            continue
        pr, subject, body, selector, repo = message
        doc = reaches_kit(cwd)
        if not doc:
            continue
        reasons = []
        if subject is not None:
            text = subject + ("\n\n" + body if body else "")
            problems = message_problems(text, pr)
            if problems:
                reasons.append(message_reason(problems, doc))
        else:
            text = body
        try:
            missing = missing_credit_lines(text, selector, repo, cwd)
        except Exception:  # noqa: BLE001 - registered `|| true`, so a crash would let the merge through
            missing = None
        if missing is None:
            reasons.append(lookup_reason(doc))
        elif missing:
            reasons.append(credit_reason(missing, doc))
        if reasons:
            deny("\n\n".join(reasons))
            return


def merge_message(args, bodies, cwd):
    """The (PR number or "any", subject, body, PR selector, repo) a `gh pr merge` would write, or None.

    The subject and body are None where the command gives none, and the
    selector and repo where it names none. None overall when the command gives
    neither subject nor body - GitHub then builds the message, and CI checks
    the PR title - or when a value can't be read.
    """
    subject = body = selector = repo = None
    pr = "any"
    index = 0
    while index < len(args):
        arg = args[index]
        flag, sep, inline = arg.partition("=")
        if flag in VALUE_FLAGS:
            if sep:
                value = inline
            elif index + 1 < len(args):
                index += 1
                value = args[index]
            else:
                return None
            if flag in {"--subject", "-t"}:
                subject = value
            elif flag in {"--body", "-b"}:
                body = value
            elif flag in {"--repo", "-R"}:
                repo = value
            elif flag in {"--body-file", "-F"}:
                body = read_body_file(value, bodies, cwd)
                if body is None:
                    return None
        elif not arg.startswith("-"):
            selector = arg
            number = re.fullmatch(r"#?(\d+)|.*/pull/(\d+)/?", arg)
            if number:
                pr = number[1] or number[2]
        index += 1
    # A `$` or backtick in the subject means the shell rewrites it first.
    if (subject is None and body is None) or (subject and re.search(r"[$`]", subject)):
        return None
    return pr, subject, body, selector, repo


def read_body_file(path, bodies, cwd):
    """A `--body-file`'s text - the command's heredoc for `-` - or None."""
    if path == "-":
        return bodies[0] if len(bodies) == 1 else None
    try:
        with open(os.path.join(cwd, path), encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


def missing_credit_lines(text, selector, repo, cwd):
    """The `Co-authored-by` lines `text` lacks ([] when none), or None when the PR can't be read."""
    deadline = time.monotonic() + GH_TOTAL
    view = ["pr", "view", *([selector] if selector else []), *(["-R", repo] if repo else [])]
    raw = gh(cwd, deadline, *view, "--json", "author,commits")
    try:
        data = json.loads(raw or "")
        author = data["author"]["login"]
        commit_authors = [a for commit in data["commits"] for a in commit["authors"]]
    except (ValueError, KeyError, TypeError):
        return None
    if not isinstance(author, str) or not author:
        return None
    if not all(isinstance(a, dict) and isinstance(a.get("login") or "", str) for a in commit_authors):
        return None
    lines = []
    for login, name in credited_authors(author, commit_authors, text):
        found = gh(cwd, deadline, "api", f"users/{login}", "-q", ".id")
        user_id = found.strip() if found and found.strip().isdigit() else "<id>"
        lines.append(f"Co-authored-by: {name} <{user_id}+{login}@users.noreply.github.com>")
    return lines


def credited_authors(pr_author, commit_authors, text):
    """The (login, name) of each commit author, other than the PR's, `text` doesn't credit.

    A credit counts only in the message's last paragraph, where git reads
    trailers. An author with no login gets no line, as git.md says. Logins
    compare without regard to case, as GitHub's do.
    """
    trailers = re.split(r"\n[ \t]*\n", text.strip())[-1]
    seen = {pr_author.lower()}
    missing = []
    for author in commit_authors:
        login = author.get("login")
        if not login or login.lower() in seen:
            continue
        seen.add(login.lower())
        trailer = rf"^Co-authored-by:.*<\d+\+{re.escape(login)}@users\.noreply\.github\.com>[ \t]*$"
        if not re.search(trailer, trailers, re.IGNORECASE | re.MULTILINE):
            missing.append((login, author.get("name") or login))
    return missing


def credit_reason(lines, doc):
    """A refusal naming each credit line the squash message needs."""
    listed = "\n".join(f"- {line}" for line in lines)
    return (
        f"The squash message lacks credit for commit authors other than the PR's. "
        f"Add, after a blank line below any `Closes` lines:\n{listed}\n"
        f"See the Squash credit rule in {doc}."
    )


def lookup_reason(doc):
    """A refusal for a merge whose PR authors couldn't be read, so its credit lines can't be checked."""
    return (
        "Couldn't read the PR's authors from `gh pr view`, so the squash credit lines "
        "can't be checked, and a squash commit can't be amended once merged. "
        f"Check that `gh` is installed, signed in and online, then retry the merge. See {doc}."
    )


def gh(cwd, deadline, *args):
    """Run a `gh` command, returning stdout, or None if it failed or ran out of time.

    The lookup gets GH_TIMEOUT seconds, or what is left before `deadline` (a
    time.monotonic() value) if that is less.
    """
    left = min(GH_TIMEOUT, deadline - time.monotonic())
    if left <= 0:
        return None
    try:
        done = subprocess.run(("gh", *args), cwd=cwd, capture_output=True, text=True, check=False, timeout=left)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


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
