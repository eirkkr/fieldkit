#!/usr/bin/env python3
"""PreToolUse hook: refuse an edit in a kit repo's main checkout on its default branch.

`KIT.md` says a session makes a worktree before its first edit to a file git
does not ignore. As prose that has failed: sessions edited in the main
checkout, and other sessions' work shared its tree. This hook refuses an
`Edit`, `Write` or `NotebookEdit` of a file when all of these hold:

- the repo reaches the kit - it has a `.fieldkit` entry at its root, or is the
  kit itself (`reaches_kit` in conventions.py);
- the file's own worktree is the main one, not a linked worktree - judged by
  where the file is, not by where the session is, so a consumer session
  editing a file in the kit is judged by the kit;
- that worktree has the default branch checked out, the default being
  `fieldkit.defaultBranch`, else `origin/HEAD`, else `main` - the order
  `hooks/pre-commit` reads it in, so change both together;
- git does not ignore the file, which leaves Claude Code's own worktrees
  (under the gitignored `.claude/worktrees/`) and any other ignored file free;
- `fieldkit.allowMainEdits` is not `true` in the repo's git config.

Anything else, and anything it cannot read - an odd payload, a git failure, a
file outside any repo - is let through: a missed refusal is no worse than no
hook, while a false one blocks legitimate work. Edits made through a shell
command are not seen. See ADR 073 under docs/decisions/.

Registered in ~/.claude/settings.json by `just install`
(scripts/register-hooks.sh); not meant to be invoked directly. Refuses through
PreToolUse's JSON `deny`, never an exit code, and the registration appends
`|| true` so a crash fails open. Standard library only - it runs in whatever
repo the session is in, so it must not depend on that repo's toolchain.
"""

import json
import os
import subprocess
import sys

from conventions import git, reaches_kit

TOOLS = {"Edit", "Write", "NotebookEdit"}
SWITCH = "fieldkit.allowMainEdits"


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(payload, dict) or payload.get("tool_name") not in TOOLS:
        return
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(path, str) or not path:
        return

    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    target = os.path.realpath(os.path.join(cwd, os.path.expanduser(path)))
    directory = existing_directory(target)
    if directory is None:
        return

    doc = reaches_kit(directory)
    if not doc:
        return
    git_dir = absolute_dir(directory, "--git-dir")
    common_dir = absolute_dir(directory, "--git-common-dir")
    if not git_dir or git_dir != common_dir:
        return
    branch = (git(directory, "symbolic-ref", "--quiet", "--short", "HEAD") or "").strip()
    if not branch or branch != default_branch(directory):
        return
    if is_ignored(directory, target) is not False:
        return
    if (git(directory, "config", "--type=bool", "--get", SWITCH) or "").strip() == "true":
        return

    # A kit file edited from a session whose own repo is another one: the
    # creation script run from that session would make the other repo's sibling.
    from_elsewhere = not doc.startswith(".fieldkit") and absolute_dir(cwd, "--git-common-dir") != common_dir
    deny(reason(branch, doc, from_elsewhere))


def existing_directory(path):
    """The nearest directory at or above `path`, which a new file's may not have."""
    path = os.path.dirname(path)
    while not os.path.isdir(path):
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent
    return path


def absolute_dir(directory, flag):
    """What `git rev-parse <flag>` names from `directory`, resolved, or None."""
    out = git(directory, "rev-parse", "--path-format=absolute", flag)
    return os.path.realpath(out.strip()) if out and out.strip() else None


def default_branch(directory):
    """The default branch, read as `hooks/pre-commit` reads it."""
    name = (git(directory, "config", "--get", "fieldkit.defaultBranch") or "").strip()
    if not name:
        name = (git(directory, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD") or "").strip()
        name = name.removeprefix("origin/")
    return name or "main"


def is_ignored(directory, target):
    """True if git ignores `target`, False if not, None if git could not say."""
    try:
        done = subprocess.run(
            ("git", "check-ignore", "-q", "--", target),
            cwd=directory,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None
    return {0: True, 1: False}.get(done.returncode)


def reason(branch, doc, from_elsewhere):
    """The refusal: why, how to get a worktree, and how to switch the hook off."""
    base = f"This file is in a repo's main checkout, on its default branch `{branch}`. "
    if from_elsewhere:
        return (
            base
            + "It is in the kit, which this session is not in. Do not edit it here: "
            "ask the reviewer to open a session in a kit worktree, and say what "
            "the change is."
        )
    script = ".fieldkit/scripts/new-worktree.sh" if doc.startswith(".fieldkit") else "scripts/new-worktree.sh"
    return (
        base
        + f"Create a worktree first. From the main checkout run `{script} <type> <description>`, "
        "then `EnterWorktree` the path it prints. Exit 3 means the worktree exists but its "
        "setup failed: enter it and tell the reviewer. Any other failure, or a refused entry: "
        "stop and tell the reviewer. `--existing <branch>` in place of both arguments makes the "
        "worktree for a branch no worktree has. Only if the reviewer says so, "
        f"`git config {SWITCH} true` in this repo switches this refusal off. See {doc}."
    )


def deny(why):
    """Refuse the tool call through PreToolUse's documented JSON decision."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": why,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
