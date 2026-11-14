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
- the repo has a commit (an unborn HEAD is let through: the creation script
  needs `origin/<default>`, so a fresh repo has no way to follow the refusal);
- `fieldkit.allowMainEdits` is not a git-config true in the repo (a value git
  cannot read as a boolean counts as off, so the edit is refused).

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
    if git(directory, "rev-parse", "--verify", "--quiet", "HEAD") is None:
        return
    if is_ignored(directory, target) is not False:
        return
    if (git(directory, "config", "--type=bool", "--get", SWITCH) or "").strip() == "true":
        return

    top = (git(directory, "rev-parse", "--show-toplevel") or "").strip()
    deny(reason(branch, doc, top, session_relation(cwd, common_dir, git_dir, top, target)))


def session_relation(cwd, common_dir, git_dir, top, target):
    """How the session relates to the file's repo: what the refusal should say.

    Returns ("same", None) for a session in the main checkout, or whose repo
    cannot be read; ("other", None) for one in another repo, where the creation
    script would make that repo's sibling; and ("worktree", path) for one in a
    linked worktree of this repo, with `target`'s path in that worktree.
    """
    session_common = absolute_dir(cwd, "--git-common-dir")
    if session_common is None:
        return "same", None
    if session_common != common_dir:
        return "other", None
    session_git = absolute_dir(cwd, "--git-dir")
    session_top = (git(cwd, "rev-parse", "--show-toplevel") or "").strip()
    if session_git and session_git != git_dir and session_top and top:
        return "worktree", os.path.join(os.path.realpath(session_top), os.path.relpath(target, top))
    return "same", None


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
            # A repo's own `core.fsmonitor` is a command git runs when it
            # refreshes the index; the file's repo is not one the user chose.
            ("git", "-c", "core.fsmonitor=false", "check-ignore", "-q", "--", target),
            cwd=directory,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return {0: True, 1: False}.get(done.returncode)


def reason(branch, doc, top, relation):
    """The refusal: why, what to do instead, and how to switch the hook off."""
    kind, path = relation
    kit = not doc.startswith(".fieldkit")
    base = f"This file is in a repo's main checkout, on its default branch `{branch}`. "
    switch = f"Only if the reviewer says so, `git -C {top} config {SWITCH} true` switches this refusal off for that repo."
    if kind == "worktree":
        return (
            base
            + f"This session is already in a worktree of that repo: edit the same file there, at `{path}`, "
            "and make no second worktree. " + switch
        )
    if kind == "other":
        where = "a kit worktree" if kit else "a worktree of that repo"
        return (
            base
            + f"It is not in this session's repo, so the creation script run here would make the wrong repo's worktree. "
            f"Do not edit it here: ask the reviewer to open a session in {where}, and say what the change is. " + switch
        )
    script = "scripts/new-worktree.sh" if kit else ".fieldkit/scripts/new-worktree.sh"
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
