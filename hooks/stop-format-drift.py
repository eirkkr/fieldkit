#!/usr/bin/env python3
"""Stop hook: fix, then catch formatter drift left uncommitted at turn end.

Two steps in one process, because Claude Code runs all of an event's hooks in
parallel - as separate hooks these would race:

1. If the repo names one in `fieldkit.fixCommand` (git config), run it. Its
   output is discarded, never fed back to the agent - see ADR 007.
2. Block the stop when the working tree holds changes to files the session's
   own last commit included that Claude did not make itself. That's the
   signature of a formatter or linter - step 1's, or an editor's format-on-save
   - rewriting already-committed work and orphaning the diff.

The drift check never formats and never commits; it hands the judgement back to
Claude. See ADR 024 and ADR 007 under docs/decisions/.

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

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
FIX_CONFIG = "fieldkit.fixCommand"
FIX_TIMEOUT = 120


REASON = """\
Uncommitted changes are sitting in files your own last commit already included, \
and you did not edit them yourself since committing:

{files}

A formatter or linter rewrote them after you committed. Don't run a formatter \
or linter yourself. Instead:

1. Read the diff: `git diff -- {first}`
2. If it is more than whitespace, re-run the tests it could affect.
3. Commit it (e.g. `style: format {first}`) and push, through the `push` skill \
if this repo has it.

If it isn't formatter output - you meant to leave it uncommitted, or something \
else wrote it - say so in one line and finish without committing."""


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


def snapshot(root):
    """Working-tree content: the tracked diff plus untracked file digests.

    Untracked files are hashed because `git diff` says nothing about them, and
    a fixer may well rewrite a file that isn't committed yet.
    """
    digest = hashlib.sha1(usedforsecurity=False)
    digest.update((git(root, "diff", "--no-color") or "").encode())
    for name in sorted(paths(git(root, "ls-files", "--others", "--exclude-standard"))):
        digest.update(name.encode())
        try:
            with open(os.path.join(root, name), "rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    digest.update(chunk)
        except OSError:
            continue
    return digest.hexdigest()


def run_fixer(root):
    """Run the repo's configured fix command; True if it changed anything.

    Output is deliberately discarded: ADR 007 keeps lint and format output away
    from the agent, and a failing fixer must not block the turn.
    """
    command = (git(root, "config", FIX_CONFIG) or "").strip()
    if not command:
        return False
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
        return False
    return snapshot(root) != before


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


def edited_since(transcript, since, root):
    """Repo-relative paths Claude wrote after `since`, including subagents'."""
    written = set()
    for entry in entries(transcript):
        stamp = timestamp(entry)
        if stamp is None or stamp <= since:
            continue
        message = entry.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if block.get("name") not in EDIT_TOOLS:
                continue
            target = (block.get("input") or {}).get("file_path")
            if not isinstance(target, str):
                continue
            relative = os.path.relpath(os.path.realpath(target), root)
            if not relative.startswith(".."):
                written.add(relative)
    return written


def drifted_files(root, transcript):
    """Files a formatter rewrote after this session committed them.

    A file Claude edited itself since that commit is ordinary uncommitted work,
    not drift - that's what keeps this from firing on every editing turn.
    """
    head_time = git(root, "log", "-1", "--format=%ct")
    if head_time is None:
        return []

    started = session_start(transcript) if transcript else None
    head_time = int(head_time.strip())
    # HEAD predates the session, so nothing here was committed by this turn's
    # work - a dirty tree is the user's own in-progress state, not drift.
    if started is None or head_time < started:
        return []

    committed = paths(git(root, "show", "--name-only", "--format=", "HEAD"))
    drifted = paths(git(root, "diff", "--name-only", "HEAD")) & committed
    if not drifted:
        return []
    return sorted(drifted - edited_since(transcript, head_time, root))


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
    # have drifted. Every check below only runs on a turn that left changes.
    if not (git(root, "status", "--porcelain") or "").strip():
        return

    result = {}
    if run_fixer(root):
        result["systemMessage"] = f"Applied fixes ({FIX_CONFIG})"

    files = drifted_files(root, payload.get("transcript_path"))
    if files:
        listing = "\n".join("  " + name for name in files)
        result["decision"] = "block"
        result["reason"] = REASON.format(files=listing, first=files[0])

    if result:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
