"""Set up how Claude Code creates new worktrees, in ~/.claude/settings.json.

Pins worktree.baseRef to "fresh" (branch from the remote default branch) and
adds ".fieldkit" to worktree.symlinkDirectories (a worktree has only tracked
files, and a consumer repo gitignores its .fieldkit link). Run via
`just install` (scripts/configure-worktree.sh); not meant to be invoked
directly.
"""

import json

import settings_edit

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


def main() -> None:
    old_text, data = settings_edit.load()

    safe, full = plan(data)
    if full == data:
        print("worktree settings already set in ~/.claude/settings.json, no change")
        return

    if safe != data:
        settings_edit.write(safe)
        print("Updated worktree settings in ~/.claude/settings.json")
        if full == safe:
            return

    rest = "the rest of " if safe != data else ""
    settings_edit.confirm_and_write(
        # Nothing written yet: diff against the file itself, so a reformat shows.
        old_text if safe == data else settings_edit.dump(safe),
        full,
        "Replace it with the kit's worktree settings?",
        heading=f"worktree is set to {json.dumps(safe.get('worktree'))} in ~/.claude/settings.json:",
        skipped=f"Skipped - left {rest}~/.claude/settings.json unchanged",
    )


if __name__ == "__main__":
    main()
