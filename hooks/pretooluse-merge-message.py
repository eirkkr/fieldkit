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
import sys

from conventions import heredocs, message_problems, message_reason, reaches_kit, segments


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
        pr, text = message
        problems = message_problems(text, pr)
        doc = reaches_kit(cwd) if problems else None
        if doc:
            deny(message_reason(problems, doc))
            return


def merge_message(args, bodies, cwd):
    """The (PR number or "any", message) a `gh pr merge` would write, or None.

    None when there's no `--subject` - GitHub then uses the PR title - or when
    a value can't be read.
    """
    subject = body = None
    pr = "any"
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
            number = re.fullmatch(r"#?(\d+)|.*/pull/(\d+)/?", arg)
            if number:
                pr = number[1] or number[2]
        index += 1
    # A `$` or backtick in the subject means the shell rewrites it first.
    if subject is None or re.search(r"[$`]", subject):
        return None
    return pr, subject + ("\n\n" + body if body else "")


def read_body_file(path, bodies, cwd):
    """A `--body-file`'s text - the command's heredoc for `-` - or None."""
    if path == "-":
        return bodies[0] if len(bodies) == 1 else None
    try:
        with open(os.path.join(cwd, path), encoding="utf-8") as handle:
            return handle.read()
    except OSError:
        return None


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
