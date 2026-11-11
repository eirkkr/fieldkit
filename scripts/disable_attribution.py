"""Disable Claude Code's commit/PR AI attribution in ~/.claude/settings.json.

Run via `just install` (scripts/disable-attribution.sh); not meant to be
invoked directly.
"""

import settings_edit

DISABLED = {"commit": "", "pr": "", "sessionUrl": False}


def main() -> None:
    old_text, data = settings_edit.load()

    existing_attribution = data.get("attribution")
    if not isinstance(existing_attribution, dict):
        existing_attribution = {}

    if all(existing_attribution.get(k) == v for k, v in DISABLED.items()):
        print("Attribution already disabled in ~/.claude/settings.json, no change")
        return

    new_data = dict(data)
    new_data["attribution"] = {**existing_attribution, **DISABLED}

    if old_text is None:
        settings_edit.create(new_data, "Created ~/.claude/settings.json with attribution disabled")
        return

    settings_edit.confirm_and_write(old_text, new_data, "Apply this change to disable AI attribution?")


if __name__ == "__main__":
    main()
