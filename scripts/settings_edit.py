"""The confirm-and-write flow the settings scripts share.

Each script decides what the new ~/.claude/settings.json should be and when
to ask; this module loads the file, shows the diff, takes the answer (EOF
counts as N) and writes. Imported as a sibling module: the running script's directory is on
`sys.path`, so the callers must stay in `scripts/` and be run as scripts
(`uv run python scripts/<name>.py`), not with `-m`. Not meant to be run.
"""

import difflib
import json
import pathlib

SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"
LABEL = "~/.claude/settings.json"
DIFFERS = f"{LABEL} already exists and differs from the expected result:"


def load() -> tuple[str | None, dict]:
    """The file's text (None if absent) and its parsed settings.

    Exits if the file isn't valid JSON, or holds JSON that isn't an object.
    """
    old_text = SETTINGS.read_text() if SETTINGS.exists() else None
    try:
        data = json.loads(old_text) if old_text is not None else {}
    except json.JSONDecodeError as err:
        raise SystemExit(f"{LABEL} isn't valid JSON ({err}); fix it by hand and re-run") from err
    if not isinstance(data, dict):
        raise SystemExit(f"{LABEL} isn't a JSON object; fix it by hand and re-run")
    return old_text, data


def dump(data: dict) -> str:
    return json.dumps(data, indent=2) + "\n"


def write(data: dict) -> None:
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(dump(data))


def create(data: dict, message: str) -> None:
    """Write a file that did not exist, without asking."""
    write(data)
    print(message)


def confirm_and_write(
    current_text: str,
    new_data: dict,
    question: str,
    *,
    heading: str = DIFFERS,
    skipped: str = f"Skipped - left {LABEL} unchanged",
) -> None:
    """Show the diff from `current_text` to `new_data`, ask, then write or skip.

    `heading` and `skipped` default to the whole-file wording; override them
    when the caller has already written part of the change.
    """
    diff = difflib.unified_diff(
        current_text.splitlines(keepends=True),
        dump(new_data).splitlines(keepends=True),
        fromfile=f"current {LABEL}",
        tofile=f"proposed {LABEL}",
    )
    print(heading)
    print("".join(diff))
    try:
        reply = input(f"{question} [y/N] ").strip().lower()
    except EOFError:  # no terminal: take the default, N
        print()
        reply = ""
    if reply == "y":
        write(new_data)
        print(f"Updated {LABEL}")
    else:
        print(skipped)
