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


def plan(data: dict) -> tuple[dict, bool]:
    """Return the settings with both worktree keys set, and whether doing so
    replaces a value the user holds.

    Adding an entry to a list, or filling a missing or null key, replaces
    nothing. A non-object `worktree`, another baseRef, or a
    symlinkDirectories that is not a list would be discarded, so that asks.
    """
    raw = data.get("worktree")
    worktree = dict(raw) if isinstance(raw, dict) else {}
    replaces = "worktree" in data and not isinstance(raw, dict)

    base = worktree.get("baseRef")
    if base != PINNED:
        replaces = replaces or base is not None
        worktree["baseRef"] = PINNED

    links = worktree.get("symlinkDirectories")
    if links is None:
        worktree["symlinkDirectories"] = [LINKED]
    elif not isinstance(links, list):
        replaces = True
        worktree["symlinkDirectories"] = [LINKED]
    elif LINKED not in links:
        worktree["symlinkDirectories"] = [*links, LINKED]

    return {**data, "worktree": worktree}, replaces


def main() -> None:
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    new_data, replaces = plan(data)
    if new_data == data:
        print("worktree settings already set in ~/.claude/settings.json, no change")
        return

    new_text = json.dumps(new_data, indent=2) + "\n"

    if not replaces:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(new_text)
        print("Set worktree.baseRef and worktree.symlinkDirectories in ~/.claude/settings.json")
        return

    diff = difflib.unified_diff(
        (old_text or "").splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print(f"worktree is set to {data.get('worktree')!r} in ~/.claude/settings.json:")
    print("".join(diff))
    try:
        reply = input("Apply the worktree settings (base branch, .fieldkit link)? [y/N] ").strip().lower()
    except EOFError:  # no terminal: take the default, N
        print()
        reply = ""
    if reply == "y":
        SETTINGS.write_text(new_text)
        print("Updated ~/.claude/settings.json")
    else:
        print("Skipped - left ~/.claude/settings.json unchanged")


if __name__ == "__main__":
    main()
