#!/usr/bin/env python3
"""Stop hook: run the repo's auto-fixer at turn end and report what it changed.

Two steps in one process, because Claude Code runs all of an event's hooks in
parallel - as separate hooks these would race:

1. If the repo names one in `fieldkit.fixCommand` (git config), run it. Its
   output is discarded, never fed back to the agent - see ADR 007. The working
   tree is digested either side of the run, so which files the fixer rewrote is
   measured rather than inferred. Both digests are taken against one pinned
   commit, so a commit landing mid-run can't make an untouched file read as
   rewritten.
2. Block the stop when it rewrote anything, splitting the files two ways: those
   that matched the baseline until the fixer touched them, whose reformat the
   commit they came from no longer carries, and those already differing from it,
   whose reformat joins the uncommitted work around them.

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
MOVED = (
    "A commit landed while the fixer ran, so both groups are measured against "
    "the commit before it and a path may sit in the wrong one."
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


def paths(output):
    """The non-empty lines of a git command's output, as a set."""
    return {line for line in (output or "").splitlines() if line}


def head(root):
    """The current commit, or the literal "HEAD" when the repo has none.

    Both snapshots and the split diff against this one value, so a commit
    landing mid-run can't shift the baseline under the comparison. The literal
    stands in for a repo with nothing committed: it makes those git calls fail
    exactly as they would have anyway, leaving every path to the untracked pass.
    """
    return (git(root, "rev-parse", "HEAD") or "HEAD").strip()


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


def snapshot(root, base):
    """Digest every file that differs from `base` or isn't tracked.

    A file matching `base` needs no entry, and its absence is the signal: should
    the fixer rewrite one, it starts differing and appears in the second
    snapshot alone. That is exactly the set whose reformat a commit has been
    left behind by.

    `base` is a resolved commit rather than `HEAD` so that both snapshots share
    one baseline. Against a moving `HEAD` a file could leave the second snapshot
    only because something committed it, which reads identically to the fixer
    having rewritten it.
    """
    names = paths(git(root, "diff", "--name-only", base))
    names |= paths(git(root, "ls-files", "--others", "--exclude-standard"))
    return {name: digest(os.path.join(root, name)) for name in names}


def run_fixer(root, base):
    """Run the repo's configured fix command.

    Returns the command, every path it rewrote, and the subset it dirtied from a
    clean state. Output is deliberately discarded: ADR 007 keeps lint and format
    output away from the agent, and a failing fixer must not block the turn.
    """
    command = (git(root, "config", FIX_CONFIG) or "").strip()
    if not command:
        return "", set(), set()
    before = snapshot(root, base)
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
    after = snapshot(root, base)
    rewritten = {n for n in set(before) | set(after) if before.get(n) != after.get(n)}
    return command, rewritten, set(after) - set(before)


def split(root, base, rewritten, dirtied):
    """The rewritten paths, split into committed and uncommitted content.

    A path the fixer dirtied that `base` also tracks was carrying committed
    content until the fix landed, so that commit is now missing it. Everything
    else was already uncommitted - modified, or not tracked at all - and the
    reformat simply joins it.
    """
    tracked = paths(git(root, "ls-tree", "-r", "--name-only", base))
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

    base = head(root)
    command, rewritten, dirtied = run_fixer(root, base)
    if not rewritten:
        return

    committed, uncommitted = split(root, base, rewritten, dirtied)
    lines = [f"`{command}` rewrote these files:", ""]
    lines += listing(COMMITTED, committed)
    lines += listing(UNCOMMITTED, uncommitted)
    if head(root) != base:
        lines.append(MOVED)

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
