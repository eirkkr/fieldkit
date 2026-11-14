"""Test what scripts/register_hooks.py writes into the Claude settings.

Run via `just test-register-hooks`. Points settings_edit.SETTINGS at a scratch
file, so ~/.claude/settings.json is never read or written. The expected
matchers and files are written out here, not read from HOOKS, so a changed
matcher or a dropped hook fails the test.
"""

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import register_hooks  # noqa: E402
import settings_edit  # noqa: E402

KIT = "/kit"

# event, matcher (None: the group carries none), file
EXPECTED = (
    ("Stop", None, "stop-autofix.py"),
    ("PreToolUse", "Bash", "pretooluse-branch-name.py"),
    ("PreToolUse", "Bash", "pretooluse-merge-message.py"),
    ("PreToolUse", "Edit|Write|NotebookEdit", "pretooluse-worktree-edit.py"),
)


class RegisterHooksTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.settings = pathlib.Path(tmp.name) / "settings.json"
        old = settings_edit.SETTINGS, sys.argv
        settings_edit.SETTINGS, sys.argv = self.settings, ["register_hooks.py", KIT]
        self.addCleanup(lambda: (setattr(settings_edit, "SETTINGS", old[0]), setattr(sys, "argv", old[1])))

    def register(self) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            register_hooks.main()
        return out.getvalue()

    def groups(self, event: str) -> list[dict]:
        return json.loads(self.settings.read_text())["hooks"][event]

    def test_every_hook_is_registered_with_its_matcher_and_command(self) -> None:
        self.register()
        for event, matcher, file in EXPECTED:
            command = f"python3 {KIT}/hooks/{file} || true"
            found = [
                group
                for group in self.groups(event)
                if [entry["command"] for entry in group["hooks"]] == [command]
            ]
            self.assertEqual(len(found), 1, f"{event} {file}: want one group running {command!r}")
            self.assertEqual(found[0].get("matcher"), matcher, f"{file}: matcher")
            self.assertEqual(found[0]["hooks"][0]["type"], "command", f"{file}: type")

    def test_the_registered_hooks_are_exactly_the_expected_ones(self) -> None:
        self.assertEqual(
            sorted(((h.event, h.matcher, h.file) for h in register_hooks.HOOKS), key=str),
            sorted(EXPECTED, key=str),
        )

    def test_a_second_run_changes_nothing(self) -> None:
        self.register()
        first = self.settings.read_text()
        self.assertIn("no change", self.register())
        self.assertEqual(self.settings.read_text(), first)

    def test_a_moved_kit_rewrites_the_command_in_place(self) -> None:
        self.register()
        sys.argv = ["register_hooks.py", "/moved"]
        with mock.patch("builtins.input", return_value="y"):
            self.register()
        commands = [e["command"] for g in self.groups("PreToolUse") for e in g["hooks"]]
        self.assertEqual(len(commands), 3)
        self.assertTrue(all(c.startswith("python3 /moved/hooks/") and c.endswith(" || true") for c in commands))


if __name__ == "__main__":
    unittest.main(verbosity=1)
