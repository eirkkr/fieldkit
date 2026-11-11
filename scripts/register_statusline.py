"""Point ~/.claude/settings.json's statusLine at the kit's linked script.

Run via `just install` (scripts/register-statusline.sh); not meant to be
invoked directly.
"""

import settings_edit

STATUS_LINE = {"type": "command", "command": "bash ~/.claude/statusline-command.sh"}


def main() -> None:
    old_text, data = settings_edit.load()

    if data.get("statusLine") == STATUS_LINE:
        print("statusLine already set in ~/.claude/settings.json, no change")
        return

    new_data = dict(data)
    new_data["statusLine"] = STATUS_LINE

    if old_text is None:
        settings_edit.create(new_data, "Created ~/.claude/settings.json with statusLine set")
        return

    settings_edit.confirm_and_write(old_text, new_data, "Apply this change to set statusLine?")


if __name__ == "__main__":
    main()
