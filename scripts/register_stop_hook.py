"""Register the kit's format-drift Stop hook in ~/.claude/settings.json.

Run via `just install` (scripts/register-stop-hook.sh); not meant to be invoked
directly. Takes the kit directory as its one argument.
"""

import difflib
import json
import pathlib
import sys

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
HOOK_FILE = "stop-format-drift.py"


def command_for(kit: str) -> str:
    """The registered command, made unable to wedge a session.

    A `Stop` hook exiting non-zero is read as a blocking error, and the hook
    signals a real block through JSON on stdout rather than its exit code. So
    any non-zero exit is a malfunction - a checked-out branch predating the
    hook file, an unreadable clone, a crash - and `|| true` keeps it inert
    instead of refusing to end every turn.
    """
    return f"python3 {kit}/hooks/{HOOK_FILE} || true"


def with_hook(data: dict, command: str) -> dict | None:
    """Settings with the Stop hook registered, or None if it already is.

    Rewrites an existing entry in place when the kit has moved, so a relocated
    clone doesn't leave a dead command behind, and leaves any other Stop hooks
    the user has alone.
    """
    new_data = json.loads(json.dumps(data))
    groups = new_data.setdefault("hooks", {}).setdefault("Stop", [])
    if not isinstance(groups, list):
        raise SystemExit("hooks.Stop in ~/.claude/settings.json isn't a list")

    for group in groups:
        for hook in (group or {}).get("hooks", []):
            if HOOK_FILE not in str(hook.get("command", "")):
                continue
            if hook["command"] == command:
                return None
            hook["command"] = command
            return new_data

    # Stop ignores the matcher field, so the group carries only its hooks.
    groups.append({"hooks": [{"type": "command", "command": command}]})
    return new_data


def main() -> None:
    command = command_for(sys.argv[1].rstrip("/"))
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    new_data = with_hook(data, command)
    if new_data is None:
        print("Format-drift Stop hook already registered in ~/.claude/settings.json, no change")
        return
    new_text = json.dumps(new_data, indent=2) + "\n"

    if old_text is None:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(new_text)
        print("Created ~/.claude/settings.json with the format-drift Stop hook")
        return

    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print("~/.claude/settings.json already exists and differs from the expected result:")
    print("".join(diff))
    reply = input("Apply this change to register the format-drift Stop hook? [y/N] ").strip().lower()
    if reply == "y":
        SETTINGS.write_text(new_text)
        print("Updated ~/.claude/settings.json")
    else:
        print("Skipped - left ~/.claude/settings.json unchanged")


if __name__ == "__main__":
    main()
