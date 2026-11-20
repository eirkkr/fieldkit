#!/usr/bin/env python3
"""PreToolUse hook: refuse a squash merge whose commit message breaks the kit's rules.

The kit squash-merges, so the only commit a PR leaves on the default branch is
the one `gh pr merge --subject ... --body ...` writes. This hook checks that
message before the merge runs: the subject's type, case, length and ` (#N)`
suffix, and the body's wrapping - the rules in conventions.py, next to this
file.

The body is read from `--body`/`-b`, or from `--body-file`/`-F` naming a file
or `-` fed by a heredoc. With no `--subject`, GitHub builds the subject from
the PR title, which CI checks instead, so the merge is let through. The PR
number comes from the command's argument; with none, any ` (#N)` is accepted.

It also refuses a message lacking the `Co-authored-by` line for each commit
author who isn't the PR's author (git.md's Squash credit rule). That needs the
PR's authors, so it asks `gh pr view` - the one network call a merge pays, and
a second, `gh api users/<login>`, only to word a refusal. A lookup that fails
or times out lets the merge through: the hook never blocks on a network error.

Like the branch-name hook it applies only in a repo that reaches the kit, lets
through anything it can't parse, and refuses through PreToolUse's JSON `deny`.
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

from conventions import heredocs, message_problems, message_reason, reaches_kit, segments

# Seconds a `gh` lookup may take before the merge is let through unchecked.
GH_TIMEOUT = 15


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
        pr, text, selector = message
        doc = reaches_kit(cwd)
        if not doc:
            continue
        reasons = []
        problems = message_problems(text, pr)
        if problems:
            reasons.append(message_reason(problems, doc))
        missing = missing_credit_lines(text, selector, cwd)
        if missing:
            reasons.append(credit_reason(missing, doc))
        if reasons:
            deny("\n\n".join(reasons))
            return


def merge_message(args, bodies, cwd):
    """The (PR number or "any", message, PR selector or None) a `gh pr merge` would write, or None.

    None when there's no `--subject` - GitHub then uses the PR title - or when
    a value can't be read.
    """
    subject = body = None
    pr = "any"
    selector = None
    index = 0
    while index < len(args):
        arg = args[index]
        flag, sep, inline = arg.partition("=")
        takes_value = flag in {"--subject", "-t", "--body", "-b", "--body-file", "-F"}
        if takes_value:
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
            else:
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
    if subject is None or re.search(r"[$`]", subject):
        return None
    return pr, subject + ("\n\n" + body if body else ""), selector


def read_body_file(path, bodies, cwd):
    """A `--body-file`'s text - the command's heredoc for `-` - or None."""
    if path == "-":
        return bodies[0] if len(bodies) == 1 else None
    try:
        with open(os.path.join(cwd, path), encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


def missing_credit_lines(text, selector, cwd):
    """The `Co-authored-by` lines `text` lacks, or [] when none are or a lookup fails."""
    raw = gh(cwd, "pr", "view", *([selector] if selector else []), "--json", "author,commits")
    try:
        data = json.loads(raw or "")
        author = data["author"]["login"]
        commit_authors = [a for commit in data["commits"] for a in commit["authors"]]
    except (ValueError, KeyError, TypeError):
        return []
    lines = []
    for login, name in credited_authors(author, commit_authors, text):
        found = gh(cwd, "api", f"users/{login}", "-q", ".id")
        user_id = found.strip() if found and found.strip().isdigit() else "<id>"
        lines.append(f"Co-authored-by: {name} <{user_id}+{login}@users.noreply.github.com>")
    return lines


def credited_authors(pr_author, commit_authors, text):
    """The (login, name) of each commit author, other than the PR's, `text` doesn't credit.

    An author with no login gets no line, as git.md says. Logins compare
    without regard to case, as GitHub's do.
    """
    seen = {str(pr_author).lower()}
    missing = []
    for author in commit_authors:
        if not isinstance(author, dict) or not author.get("login"):
            continue
        login = author["login"]
        if login.lower() in seen:
            continue
        seen.add(login.lower())
        trailer = rf"^Co-authored-by:.*<\d+\+{re.escape(login)}@users\.noreply\.github\.com>[ \t]*$"
        if not re.search(trailer, text, re.IGNORECASE | re.MULTILINE):
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


def gh(cwd, *args):
    """Run a `gh` command, returning stdout, or None if it failed or timed out."""
    try:
        done = subprocess.run(
            ("gh", *args), cwd=cwd, capture_output=True, text=True, check=False, timeout=GH_TIMEOUT
        )
    except (OSError, subprocess.SubprocessError):
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
