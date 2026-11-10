"""Pin new worktrees to branch from the remote default branch.

Sets worktree.baseRef to "fresh" in ~/.claude/settings.json. Run via
`just install` (scripts/pin-worktree-base.sh); not meant to be invoked
directly.
"""

import difflib
import json
import pathlib

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
PINNED = "fresh"


def main() -> None:
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    worktree = data.get("worktree")
    if not isinstance(worktree, dict):
        worktree = {}
    current = worktree.get("baseRef")

    if current == PINNED:
        print("worktree.baseRef already fresh in ~/.claude/settings.json, no change")
        return

    new_data = dict(data)
    new_data["worktree"] = {**worktree, "baseRef": PINNED}
    new_text = json.dumps(new_data, indent=2) + "\n"

    # Nothing to conflict with: no file, or no baseRef set. Write silently.
    if current is None:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(new_text)
        print("Set worktree.baseRef to fresh in ~/.claude/settings.json")
        return

    diff = difflib.unified_diff(
        (old_text or "").splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print(f"worktree.baseRef is {current!r} in ~/.claude/settings.json:")
    print("".join(diff))
    reply = input("Pin new worktrees to the remote default branch? [y/N] ").strip().lower()
    if reply == "y":
        SETTINGS.write_text(new_text)
        print("Updated ~/.claude/settings.json")
    else:
        print("Skipped - left ~/.claude/settings.json unchanged")


if __name__ == "__main__":
    main()
