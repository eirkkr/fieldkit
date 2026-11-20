"""Test the squash-credit check in hooks/pretooluse-merge-message.py.

Run via `just test-merge-message-hook`. Each case runs the hook as Claude Code
does - a JSON payload on stdin - from the kit's own directory, with a fake `gh`
first on PATH, so no network is touched. The fake answers `gh pr view` from
$FAKE_VIEW and `gh api users/<login>` with a fixed id, and fails `pr view` when
$FAKE_VIEW_FAILS is set.
"""

import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

KIT = pathlib.Path(__file__).resolve().parent.parent
HOOK = KIT / "hooks" / "pretooluse-merge-message.py"

FAKE_GH = """#!/usr/bin/env bash
case "$1 $2" in
  "pr view")
    [ -n "${FAKE_VIEW_FAILS:-}" ] && exit 1
    printf '%s' "$FAKE_VIEW" ;;
  "api users/"*) echo 4242 ;;
  *) exit 1 ;;
esac
"""

SUBJECT = "docs: add a thing (#7)"
CREDIT = "Co-authored-by: Eric <4242+human@users.noreply.github.com>"


def view(pr_author, *commit_logins):
    """The `gh pr view --json author,commits` output for these authors."""
    authors = [{"login": login, "name": login.title()} for login in commit_logins]
    return json.dumps({"author": {"login": pr_author}, "commits": [{"authors": [a]} for a in authors]})


class CreditHookTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        fake = pathlib.Path(tmp.name) / "gh"
        fake.write_text(FAKE_GH, encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.bin = tmp.name

    def run_hook(self, body, **env):
        """The hook's stdout for a `gh pr merge 7` passing `body` as the message body."""
        command = f"gh pr merge 7 --squash --subject '{SUBJECT}' --body-file - <<'EOF'\n{body}\nEOF"
        payload = {"tool_name": "Bash", "cwd": str(KIT), "tool_input": {"command": command}}
        full_env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", **env}
        done = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=full_env,
            check=True,
        )
        return done.stdout

    def reason(self, out):
        return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]

    def test_missing_credit_is_refused_naming_the_line(self) -> None:
        """A merge lacking the commit author's credit line is refused with that line spelled out."""
        out = self.run_hook("A body.", FAKE_VIEW=view("bot", "human"))
        self.assertIn("Co-authored-by: Human <4242+human@users.noreply.github.com>", self.reason(out))

    def test_credit_line_present_passes(self) -> None:
        """A message carrying the credit line, whatever the name in it, is let through."""
        out = self.run_hook(f"A body.\n\n{CREDIT}", FAKE_VIEW=view("bot", "human"))
        self.assertEqual(out, "")

    def test_credit_for_another_login_is_still_missing(self) -> None:
        """A credit line for someone else doesn't satisfy a different author."""
        other = "Co-authored-by: Z <9+other@users.noreply.github.com>"
        out = self.run_hook(f"A body.\n\n{other}", FAKE_VIEW=view("bot", "human"))
        self.assertIn("4242+human@", self.reason(out))

    def test_pr_authors_own_commits_need_no_credit(self) -> None:
        """Commits by the PR's own author, in any letter case, add no line."""
        out = self.run_hook("A body.", FAKE_VIEW=view("Human", "human"))
        self.assertEqual(out, "")

    def test_each_missing_author_is_named_once(self) -> None:
        """Two commits by one author, and a second author, give two lines."""
        out = self.run_hook("A body.", FAKE_VIEW=view("bot", "human", "human", "pair"))
        reason = self.reason(out)
        self.assertEqual(reason.count("+human@"), 1)
        self.assertEqual(reason.count("+pair@"), 1)

    def test_author_without_login_gets_no_line(self) -> None:
        """A commit author GitHub can't map to a login is not credited."""
        data = json.dumps({"author": {"login": "bot"}, "commits": [{"authors": [{"login": "", "name": "X"}]}]})
        self.assertEqual(self.run_hook("A body.", FAKE_VIEW=data), "")

    def test_failed_lookup_lets_the_merge_through(self) -> None:
        """When `gh pr view` fails the hook can't know, so it doesn't block."""
        self.assertEqual(self.run_hook("A body.", FAKE_VIEW_FAILS="1"), "")

    def test_unreadable_lookup_lets_the_merge_through(self) -> None:
        """Output that isn't the expected JSON doesn't block either."""
        self.assertEqual(self.run_hook("A body.", FAKE_VIEW="not json"), "")

    def test_message_and_credit_problems_are_reported_together(self) -> None:
        """A wrapping problem and a missing credit both appear in one refusal."""
        out = self.run_hook("word " * 20, FAKE_VIEW=view("bot", "human"))
        reason = self.reason(out)
        self.assertIn("over the 72-character wrap", reason)
        self.assertIn("4242+human@", reason)


if __name__ == "__main__":
    unittest.main()
