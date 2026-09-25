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
at its root, or the kit itself. `--name <branch>` checks one name outside
Claude Code, exiting 1 with the reason when it breaks a rule; CI runs it
through scripts/check-branch-name.sh. See ADR 046 under docs/decisions/.

Registered in ~/.claude/settings.json by `just install`
(scripts/register-hooks.sh); not meant to be invoked directly. Refuses through
PreToolUse's JSON `deny`, never an exit code, and the registration appends
`|| true` so a crash fails open. Standard library only - it runs in whatever
repo the session is in, so it must not depend on that repo's toolchain.
"""

import json
import os
import re
import shlex
import subprocess
import sys

# Mirror of conventions/git.md's Branches rules - change both together.
PREFIXES = ("feature/", "bugfix/", "hotfix/", "release/", "chore/")
MAX_LENGTH = 50

KIT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

SEPARATORS = {"&&", "||", ";", "|", "&", "\n", "(", ")", "|&", ";;"}
# Global git options that take their value as the next word.
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
# `git branch` flags that leave it creating a branch from its first positional.
BRANCH_CREATE_FLAGS = {
    "-f", "--force", "-t", "--track", "--no-track", "-q", "--quiet",
    "--create-reflog", "--recurse-submodules",
}
BRANCH_RENAME_FLAGS = {"-m", "-M", "--move", "-c", "-C", "--copy"}


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--name":
        problem = violation(sys.argv[2])
        if problem:
            sys.exit(reason(sys.argv[2], problem, "conventions/git.md"))
        return

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
        problem = violation(name)
        if not problem:
            continue
        doc = reaches_kit(directory)
        if doc:
            deny(name, problem, doc)
            return


def violation(name):
    """Why `name` breaks the rules, or None when it doesn't."""
    if not name.startswith(PREFIXES) or name in PREFIXES:
        return "has no allowed prefix"
    if len(name) > MAX_LENGTH:
        return f"is {len(name)} characters, over the {MAX_LENGTH}-character limit"
    return None


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


def segments(command):
    """Split a shell command into the word lists of its simple commands."""
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


def reaches_kit(directory):
    """git.md's path as that repo reaches it, or None if the repo doesn't.

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


def deny(name, problem, doc):
    """Refuse the tool call through PreToolUse's documented JSON decision."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason(name, problem, doc),
                }
            }
        )
    )


def reason(name, problem, doc):
    """Which rule `name` breaks, the rules in full, and where they're written."""
    allowed = ", ".join(f"`{prefix}`" for prefix in PREFIXES)
    return (
        f"Branch name `{name}` {problem}. The convention is "
        f"`type/short-description`, lowercase and hyphen-separated, with the "
        f"prefix one of {allowed}, at most {MAX_LENGTH} characters in all. "
        f"Pick a conforming name and retry - see {doc}."
    )


def git(cwd, *args):
    """Run a git command, returning stdout, or None if it failed."""
    try:
        done = subprocess.run(
            ("git", *args), cwd=cwd, capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


if __name__ == "__main__":
    main()
