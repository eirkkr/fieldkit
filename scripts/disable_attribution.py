"""Disable Claude Code's commit/PR AI attribution in ~/.claude/settings.json.

Run via `just install` (scripts/disable-attribution.sh); not meant to be
invoked directly.
"""

import difflib
import json
import pathlib

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
DISABLED = {"commit": "", "pr": "", "sessionUrl": False}


def main() -> None:
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    existing_attribution = data.get("attribution")
    if not isinstance(existing_attribution, dict):
        existing_attribution = {}

    if all(existing_attribution.get(k) == v for k, v in DISABLED.items()):
        print("Attribution already disabled in ~/.claude/settings.json, no change")
        return

    new_data = dict(data)
    new_data["attribution"] = {**existing_attribution, **DISABLED}
    new_text = json.dumps(new_data, indent=2) + "\n"

    if old_text is None:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(new_text)
        print("Created ~/.claude/settings.json with attribution disabled")
        return

    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print("~/.claude/settings.json already exists and differs from the expected result:")
    print("".join(diff))
    reply = input("Apply this change to disable AI attribution? [y/N] ").strip().lower()
    if reply == "y":
        SETTINGS.write_text(new_text)
        print("Updated ~/.claude/settings.json")
    else:
        print("Skipped - left ~/.claude/settings.json unchanged")


if __name__ == "__main__":
    main()
