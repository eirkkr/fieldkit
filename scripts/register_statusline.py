"""Point ~/.claude/settings.json's statusLine at the kit's linked script.

Run via `just install` (scripts/register-statusline.sh); not meant to be
invoked directly.
"""

import difflib
import json
import pathlib

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
STATUS_LINE = {"type": "command", "command": "bash ~/.claude/statusline-command.sh"}


def main() -> None:
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    if data.get("statusLine") == STATUS_LINE:
        print("statusLine already set in ~/.claude/settings.json, no change")
        return

    new_data = dict(data)
    new_data["statusLine"] = STATUS_LINE
    new_text = json.dumps(new_data, indent=2) + "\n"

    if old_text is None:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(new_text)
        print("Created ~/.claude/settings.json with statusLine set")
        return

    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print("~/.claude/settings.json already exists and differs from the expected result:")
    print("".join(diff))
    reply = input("Apply this change to set statusLine? [y/N] ").strip().lower()
    if reply == "y":
        SETTINGS.write_text(new_text)
        print("Updated ~/.claude/settings.json")
    else:
        print("Skipped - left ~/.claude/settings.json unchanged")


if __name__ == "__main__":
    main()
