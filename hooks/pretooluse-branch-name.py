#!/usr/bin/env python3
"""PreToolUse hook: refuse a Bash command naming a branch against the kit's rules.

`conventions/git.md` requires Conventional Branch names with a prefix from a
closed set, and caps their length. As prose, that holds only if the branching
agent read `git.md` first, and branching is too small an action to prompt the
read. This hook checks the name when the branch is made, before anything is on
it.

It catches, anywhere in a compound command:

- `git checkout -b|-B <name>`
- `git switch -c|-C|--create|--force-create <name>`
- `git branch <name>`, and `git branch -m|-M|-c|-C [<old>] <new>`
- `git worktree add -b|-B <name>`

Anything it can't read with confidence is let through - a missed catch is no
worse than having no hook, while a false refusal blocks legitimate work. That
covers unparseable shell, names built from `$VAR` or command substitution, flag
combinations it doesn't model, and `git worktree add <path>` without `-b`,
whose branch name git derives from the path only when no such branch exists.

It applies only in a repo that reaches the kit - one with a `.fieldkit` entry
at its root, or the kit itself. The rules themselves live in conventions.py,
next to this file, which CI also runs. See ADR 046 under docs/decisions/.

Registered in ~/.claude/settings.json by `just install`
(scripts/register-hooks.sh); not meant to be invoked directly. Refuses through
PreToolUse's JSON `deny`, never an exit code, and the registration appends
`|| true` so a crash fails open. Standard library only - it runs in whatever
repo the session is in, so it must not depend on that repo's toolchain.
"""

import json
import os
import re
import sys

from conventions import branch_problem, branch_reason, reaches_kit, segments

# Global git options that take their value as the next word.
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
# `git branch` flags that leave it creating a branch from its first positional.
BRANCH_CREATE_FLAGS = {
    "-f", "--force", "-t", "--track", "--no-track", "-q", "--quiet",
    "--create-reflog", "--recurse-submodules",
}
BRANCH_RENAME_FLAGS = {"-m", "-M", "--move", "-c", "-C", "--copy"}


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or "git" not in command:
        return

    cwd = payload.get("cwd") or os.getcwd()
    for directory, name in branch_names(command, cwd):
        problem = branch_problem(name)
        if not problem:
            continue
        doc = reaches_kit(directory)
        if doc:
            deny(name, problem, doc)
            return


def branch_names(command, cwd):
    """Each (directory, new branch name) the command would create or rename to."""
    for words in segments(command):
        if not words:
            continue
        if words[0] == "cd" and len(words) == 2:
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        found = git_branch_name(words, cwd)
        if found:
            yield found


def git_branch_name(words, cwd):
    """The (directory, name) a git command creates a branch as, or None."""
    while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
        words = words[1:]
    if not words or os.path.basename(words[0]) != "git":
        return None

    rest = words[1:]
    while rest and rest[0].startswith("-"):
        option = rest.pop(0)
        if option in GIT_VALUE_OPTIONS:
            if not rest:
                return None
            value = rest.pop(0)
            if option == "-C":
                cwd = os.path.join(cwd, os.path.expanduser(value))
    if not rest:
        return None

    subcommand, args = rest[0], rest[1:]
    if subcommand == "checkout":
        name = option_value(args, {"-b", "-B"})
    elif subcommand == "switch":
        name = option_value(args, {"-c", "-C", "--create", "--force-create"})
    elif subcommand == "branch":
        name = branch_command_name(args)
    elif subcommand == "worktree" and args[:1] == ["add"]:
        name = option_value(args[1:], {"-b", "-B"})
    else:
        return None

    if not name or not re.fullmatch(r"[^\s$`\\]+", name) or name.startswith("-"):
        return None
    return cwd, name


def option_value(args, flags):
    """The value of the first of `flags` in `args`, spaced or `=`-joined."""
    for index, arg in enumerate(args):
        if arg == "--":
            return None
        if arg in flags:
            return args[index + 1] if index + 1 < len(args) else None
        flag, sep, value = arg.partition("=")
        if sep and flag in flags and flag.startswith("--"):
            return value
    return None


def branch_command_name(args):
    """The branch `git branch` creates, or renames or copies to, or None.

    Any flag outside the creating and renaming sets - listing, deleting,
    upstream, or one this doesn't know - means it isn't read as creation.
    """
    flags = [arg for arg in args if arg.startswith("-")]
    positionals = [arg for arg in args if not arg.startswith("-")]
    if "--" in args:
        return None
    for flag in flags:
        if flag.split("=", 1)[0] not in BRANCH_CREATE_FLAGS | BRANCH_RENAME_FLAGS:
            return None
    if any(flag in BRANCH_RENAME_FLAGS for flag in flags):
        return positionals[-1] if positionals and len(positionals) <= 2 else None
    return positionals[0] if positionals and len(positionals) <= 2 else None


def deny(name, problem, doc):
    """Refuse the tool call through PreToolUse's documented JSON decision."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": branch_reason(name, problem, doc),
                }
            }
        )
    )


if __name__ == "__main__":
    main()
