"""Register the kit's Claude Code hooks in ~/.claude/settings.json.

Run via `just install` (scripts/register-hooks.sh); not meant to be invoked
directly. Takes the kit directory as its one argument.
"""

import difflib
import json
import pathlib
import sys
from typing import NamedTuple

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"


class Hook(NamedTuple):
    event: str
    matcher: str | None
    file: str
    # Names the hook has had before. Matched alongside the current one so a
    # rename rewrites the existing entry in place, rather than appending a
    # second group pointing at a file that no longer exists (ADR 035).
    legacy: tuple[str, ...] = ()


HOOKS = (
    Hook("Stop", None, "stop-autofix.py", ("stop-format-drift.py",)),
    Hook("PreToolUse", "Bash", "pretooluse-branch-name.py"),
)


def main() -> None:
    kit = sys.argv[1].rstrip("/")
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    data = json.loads(old_text) if old_text is not None else {}

    new_data = data
    for hook in HOOKS:
        new_data = with_hook(new_data, hook, command_for(kit, hook)) or new_data
    if new_data == data:
        print("Kit hooks already registered in ~/.claude/settings.json, no change")
        return
    new_text = json.dumps(new_data, indent=2) + "\n"

    if old_text is None:
        SETTINGS.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS.write_text(new_text)
        print("Created ~/.claude/settings.json with the kit hooks")
        return

    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile="current ~/.claude/settings.json",
        tofile="proposed ~/.claude/settings.json",
    )
    print("~/.claude/settings.json already exists and differs from the expected result:")
    print("".join(diff))
    reply = input("Apply this change to register the kit hooks? [y/N] ").strip().lower()
    if reply == "y":
        SETTINGS.write_text(new_text)
        print("Updated ~/.claude/settings.json")
    else:
        print("Skipped - left ~/.claude/settings.json unchanged")


def command_for(kit: str, hook: Hook) -> str:
    """The registered command, made unable to wedge a session.

    Each hook signals a real block through JSON on stdout rather than its exit
    code, so any non-zero exit is a malfunction - a checked-out branch
    predating the hook file, an unreadable clone, a crash. `|| true` keeps it
    inert: a `Stop` hook would otherwise refuse to end every turn, and a
    `PreToolUse` one exiting 2 would refuse every Bash call.
    """
    return f"python3 {kit}/hooks/{hook.file} || true"


def with_hook(data: dict, hook: Hook, command: str) -> dict | None:
    """Settings with the hook registered, or None if it already is.

    Rewrites an existing entry in place when the kit has moved or the hook has
    been renamed, so neither leaves a dead command behind, and leaves any other
    hooks the user has on the event alone.
    """
    new_data = json.loads(json.dumps(data))
    groups = new_data.setdefault("hooks", {}).setdefault(hook.event, [])
    if not isinstance(groups, list):
        raise SystemExit(f"hooks.{hook.event} in ~/.claude/settings.json isn't a list")

    known = (hook.file, *hook.legacy)
    for group in groups:
        for entry in (group or {}).get("hooks", []):
            registered = str(entry.get("command", ""))
            if not any(name in registered for name in known):
                continue
            if entry["command"] == command:
                return None
            entry["command"] = command
            return new_data

    group = {"hooks": [{"type": "command", "command": command}]}
    # Stop ignores the matcher field, so its group carries only its hooks.
    if hook.matcher is not None:
        group = {"matcher": hook.matcher, **group}
    groups.append(group)
    return new_data


if __name__ == "__main__":
    main()
