"""Set up how Claude Code creates new worktrees, in ~/.claude/settings.json.

Pins worktree.baseRef to "fresh" (branch from the remote default branch) and
adds ".fieldkit" to worktree.symlinkDirectories (a worktree has only tracked
files, and a consumer repo gitignores its .fieldkit link). Run via
`just install` (scripts/configure-worktree.sh); not meant to be invoked
directly.
"""

import difflib
import json
import pathlib

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
PINNED = "fresh"
LINKED = ".fieldkit"


def plan(data: dict) -> tuple[dict, dict]:
    """Return the settings with the changes that replace nothing, and with all.

    Filling a missing or null key, or adding an entry to a list, replaces
    nothing, so it is the first result and is written without asking. A
    non-object `worktree`, another baseRef, or a symlinkDirectories that is
    not a list would be discarded, so only the second result has them.
    """
    raw = data.get("worktree")
    if raw is not None and not isinstance(raw, dict):
        full = {**data, "worktree": {"baseRef": PINNED, "symlinkDirectories": [LINKED]}}
        return data, full

    safe_wt = dict(raw) if isinstance(raw, dict) else {}
    full_wt = dict(safe_wt)

    base = safe_wt.get("baseRef")
    if base is None:
        safe_wt["baseRef"] = PINNED
    full_wt["baseRef"] = PINNED

    links = safe_wt.get("symlinkDirectories")
    if links is None:
        safe_wt["symlinkDirectories"] = [LINKED]
        full_wt["symlinkDirectories"] = [LINKED]
    elif isinstance(links, list):
        if LINKED not in links:
            safe_wt["symlinkDirectories"] = [*links, LINKED]
        full_wt["symlinkDirectories"] = safe_wt["symlinkDirectories"]
    else:
        full_wt["symlinkDirectories"] = [LINKED]

    return {**data, "worktree": safe_wt}, {**data, "worktree": full_wt}


def dump(data: dict) -> str:
    return json.dumps(data, indent=2) + "\n"


def main() -> None:
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    safe, full = plan(data)
    if full == data:
        print("worktree settings already set in ~/.claude/settings.json, no change")
        return

    if safe != data:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(dump(safe))
        print("Updated worktree settings in ~/.claude/settings.json")
        if full == safe:
            return

    diff = difflib.unified_diff(
        dump(safe).splitlines(keepends=True),
        dump(full).splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print(f"worktree is set to {json.dumps(safe.get('worktree'))} in ~/.claude/settings.json:")
    print("".join(diff))
    try:
        reply = input("Replace it with the kit's worktree settings? [y/N] ").strip().lower()
    except EOFError:  # no terminal: take the default, N
        print()
        reply = ""
    if reply == "y":
        SETTINGS.write_text(dump(full))
        print("Updated ~/.claude/settings.json")
    else:
        rest = "the rest of " if safe != data else ""
        print(f"Skipped - left {rest}~/.claude/settings.json unchanged")


if __name__ == "__main__":
    main()
