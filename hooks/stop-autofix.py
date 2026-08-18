#!/usr/bin/env python3
"""Stop hook: run the repo's auto-fixer at turn end and report what it changed.

Two steps in one process, because Claude Code runs all of an event's hooks in
parallel - as separate hooks these would race:

1. If the repo names one in `fieldkit.fixCommand` (git config), run it. Its
   output is discarded, never fed back to the agent - see ADR 007. The working
   tree is digested either side of the run, so which files the fixer rewrote is
   measured rather than inferred.
2. Block the stop when it rewrote anything, splitting the files two ways: those
   that matched HEAD until the fixer touched them, whose reformat the commit
   they came from no longer carries, and those already differing from HEAD,
   whose reformat joins the uncommitted work around it.

The hook reports and stops there. It never commits, and it never says what to
do about what it found - that is Claude's call. See ADR 035, which supersedes
ADR 024, and ADR 007 under docs/decisions/.

Registered in ~/.claude/settings.json by `just install`
(scripts/register-stop-hook.sh); not meant to be invoked directly. Standard
library only - it runs in whatever repo the session is in, so it must not
depend on that repo's toolchain.
"""

import hashlib
import json
import os
import subprocess
import sys

FIX_CONFIG = "fieldkit.fixCommand"
FIX_TIMEOUT = 120

COMMITTED = "Committed - the commit these came from no longer carries the reformat:"
UNCOMMITTED = "Uncommitted - the reformat joins changes already in the working tree:"


def git(cwd, *args):
    """Run a git command, returning stdout, or None if it failed."""
    try:
        done = subprocess.run(
            ("git", *args), cwd=cwd, capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def paths(output):
    return {line for line in (output or "").splitlines() if line}


def digest(path):
    """SHA-1 of a file's bytes, or None when it can't be read."""
    sha = hashlib.sha1(usedforsecurity=False)
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                sha.update(chunk)
    except OSError:
        return None
    return sha.hexdigest()


def snapshot(root):
    """Digest every file that differs from HEAD or isn't tracked.

    A file matching HEAD needs no entry, and its absence is the signal: should
    the fixer rewrite one, it starts differing and appears in the second
    snapshot alone. That is exactly the set whose reformat a commit has been
    left behind by.
    """
    names = paths(git(root, "diff", "--name-only", "HEAD"))
    names |= paths(git(root, "ls-files", "--others", "--exclude-standard"))
    return {name: digest(os.path.join(root, name)) for name in names}


def run_fixer(root):
    """Run the repo's configured fix command.

    Returns the command, every path it rewrote, and the subset it dirtied from a
    clean state. Output is deliberately discarded: ADR 007 keeps lint and format
    output away from the agent, and a failing fixer must not block the turn.
    """
    command = (git(root, "config", FIX_CONFIG) or "").strip()
    if not command:
        return "", set(), set()
    before = snapshot(root)
    try:
        subprocess.run(
            command,
            cwd=root,
            shell=True,
            capture_output=True,
            timeout=FIX_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return command, set(), set()
    after = snapshot(root)
    rewritten = {n for n in set(before) | set(after) if before.get(n) != after.get(n)}
    return command, rewritten, set(after) - set(before)


def split(root, rewritten, dirtied):
    """The rewritten paths, split into committed and uncommitted content.

    A path the fixer dirtied that HEAD also tracks was carrying committed
    content until the fix landed, so that commit is now missing it. Everything
    else was already uncommitted - modified, or not tracked at all - and the
    reformat simply joins it.
    """
    tracked = paths(git(root, "ls-tree", "-r", "--name-only", "HEAD"))
    committed = dirtied & tracked
    return committed, rewritten - committed


def listing(heading, names):
    """A heading over its indented paths, or nothing at all when there are none."""
    if not names:
        return []
    return [heading, *("  " + name for name in sorted(names)), ""]


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return
    if not isinstance(payload, dict) or payload.get("stop_hook_active"):
        return

    root = git(payload.get("cwd") or os.getcwd(), "rev-parse", "--show-toplevel")
    if root is None:
        return
    root = os.path.realpath(root.strip())

    command, rewritten, dirtied = run_fixer(root)
    if not rewritten:
        return

    committed, uncommitted = split(root, rewritten, dirtied)
    lines = [f"`{command}` rewrote files, and the changes are uncommitted:", ""]
    lines += listing(COMMITTED, committed)
    lines += listing(UNCOMMITTED, uncommitted)

    print(
        json.dumps(
            {
                "systemMessage": f"Applied fixes ({command})",
                "decision": "block",
                "reason": "\n".join(lines).rstrip(),
            }
        )
    )


if __name__ == "__main__":
    main()
