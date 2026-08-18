#!/usr/bin/env python3
"""Stop hook: run the repo's auto-fixer at turn end and report what it changed.

Two steps in one process, because Claude Code runs all of an event's hooks in
parallel - as separate hooks these would race:

1. If the repo names one in `fieldkit.fixCommand` (git config), run it. Its
   output is discarded, never fed back to the agent - see ADR 007. The working
   tree is digested either side of the run, so which files the fixer rewrote is
   measured rather than inferred.
2. Block the stop when the fixer dirtied a file that matched HEAD and that this
   session's own last commit included. That commit no longer carries the
   reformat, and the turn is ending, so the diff would sit stranded until
   something prompts a fresh `git status`. The block states what happened and
   stops there - what to do about it is Claude's call, not the hook's.

The hook never commits and never instructs. See ADR 035, which supersedes
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
from datetime import datetime

FIX_CONFIG = "fieldkit.fixCommand"
FIX_TIMEOUT = 120


REASON = """\
`{command}` reformatted files your own last commit already included, so that \
commit no longer carries the change:

{files}

The reformat is already applied, sitting uncommitted in your working tree."""


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

    A file matching HEAD needs no entry: should the fixer rewrite one, it starts
    differing and appears in the second snapshot alone, which reads as a change
    just the same. Untracked files are included because `git diff` says nothing
    about them, and a fixer may well rewrite one that isn't committed yet.
    """
    names = paths(git(root, "diff", "--name-only", "HEAD"))
    names |= paths(git(root, "ls-files", "--others", "--exclude-standard"))
    return {name: digest(os.path.join(root, name)) for name in names}


def run_fixer(root):
    """Run the repo's configured fix command.

    Returns the command, every path it rewrote, and the subset of those it
    dirtied from a clean state. Only the last can have stranded anything: a file
    already differing from HEAD carries uncommitted work, so the reformat joins
    that and the next commit takes both.

    Output is deliberately discarded: ADR 007 keeps lint and format output away
    from the agent, and a failing fixer must not block the turn.
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
    changed = {n for n in set(before) | set(after) if before.get(n) != after.get(n)}
    return command, changed, set(after) - set(before)


def timestamp(entry):
    """Epoch seconds for a transcript entry, or None if it carries no time."""
    raw = entry.get("timestamp")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def entries(transcript):
    try:
        handle = open(transcript, encoding="utf-8")
    except OSError:
        return
    with handle:
        for line in handle:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def session_start(transcript):
    """Time of the transcript's first timestamped entry.

    The opening lines record session settings and carry no timestamp, so scan
    until one does. Returns None if the transcript is unreadable or empty.
    """
    for entry in entries(transcript):
        stamp = timestamp(entry)
        if stamp is not None:
            return stamp
    return None


def stranded(root, dirtied, transcript):
    """Fixer-dirtied paths this session's own last commit already included.

    `dirtied` holds only files that matched HEAD until the fixer rewrote them,
    so the reformat is precisely what that commit no longer carries. Both halves
    are needed: a file the session didn't commit strands nothing, and a file
    that was already dirty carries the reformat forward in the working tree.
    """
    if not dirtied:
        return []
    head_time = git(root, "log", "-1", "--format=%ct")
    started = session_start(transcript) if transcript else None
    # HEAD predates the session, so nothing here was committed by this turn's
    # work - a reformat lands in the user's own in-progress tree, not behind a
    # commit this session made.
    if head_time is None or started is None or int(head_time.strip()) < started:
        return []
    committed = paths(git(root, "show", "--name-only", "--format=", "HEAD"))
    return sorted(dirtied & committed)


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

    # One guard for both steps: a clean tree has nothing to fix and nothing to
    # have been stranded. Every check below only runs on a turn that left
    # changes.
    if not (git(root, "status", "--porcelain") or "").strip():
        return

    command, rewritten, dirtied = run_fixer(root)
    result = {}
    if rewritten:
        result["systemMessage"] = f"Applied fixes ({command})"

    files = stranded(root, dirtied, payload.get("transcript_path"))
    if files:
        listing = "\n".join("  " + name for name in files)
        result["decision"] = "block"
        result["reason"] = REASON.format(command=command, files=listing)

    if result:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
