"""Test the squash-credit check in hooks/pretooluse-merge-message.py.

Run via `just test-merge-message-hook`. Each case runs the hook as Claude Code
does - a JSON payload on stdin - with a fake `gh` first on PATH, so no network
is touched. The fake appends each call's arguments to $FAKE_LOG, answers
`gh pr view` from $FAKE_VIEW and `gh api users/<login>` with a fixed id, and
fails `pr view` when $FAKE_VIEW_FAILS is set and `api` when $FAKE_API_FAILS is.
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
echo "$*" >>"$FAKE_LOG"
case "$1 $2" in
  "pr view")
    [ -n "${FAKE_VIEW_FAILS:-}" ] && exit 1
    printf '%s' "$FAKE_VIEW" ;;
  "api users/"*)
    [ -n "${FAKE_API_FAILS:-}" ] && exit 1
    echo 4242 ;;
  *) exit 1 ;;
esac
"""

SUBJECT = "docs: add a thing (#7)"
CREDIT = "Co-authored-by: Eric <4242+human@users.noreply.github.com>"
VIEW_ARGS = "--json author,commits"


def view(pr_author, *commit_logins):
    """The `gh pr view --json author,commits` output for these authors."""
    authors = [{"login": login, "name": login.title()} for login in commit_logins]
    return json.dumps({"author": {"login": pr_author}, "commits": [{"authors": [a]} for a in authors]})


class CreditHookTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        fake = self.tmp / "gh"
        fake.write_text(FAKE_GH, encoding="utf-8")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        self.log = self.tmp / "calls.log"

    def run_command(self, command, cwd=KIT, **env):
        """The hook's stdout for `command`, run from `cwd`."""
        payload = {"tool_name": "Bash", "cwd": str(cwd), "tool_input": {"command": command}}
        full_env = {**os.environ, "PATH": f"{self.tmp}:{os.environ['PATH']}", "FAKE_LOG": str(self.log), **env}
        done = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=full_env,
            check=True,
        )
        return done.stdout

    def run_hook(self, body, flags="", **env):
        """The hook's stdout for `gh pr merge 7` with `SUBJECT` and `body`."""
        command = f"gh pr merge 7 --squash {flags} --subject '{SUBJECT}' --body-file - <<'EOF'\n{body}\nEOF"
        return self.run_command(command, **env)

    def calls(self):
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []

    def reason(self, out):
        return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]

    def test_missing_credit_is_refused_naming_the_line(self) -> None:
        """A merge lacking the commit author's credit line is refused with that line spelled out."""
        out = self.run_hook("A body.", FAKE_VIEW=view("bot", "human"))
        self.assertIn("Co-authored-by: Human <4242+human@users.noreply.github.com>", self.reason(out))

    def test_credit_line_present_passes(self) -> None:
        """A message carrying the credit line, whatever the name in it, is let through."""
        out = self.run_hook(f"A body.\n\n{CREDIT}", FAKE_VIEW=view("bot", "human"))
        self.assertEqual((out, self.calls()), ("", [f"pr view 7 {VIEW_ARGS}"]))

    def test_credit_line_outside_the_last_paragraph_is_missing(self) -> None:
        """A credit line followed by more text isn't a trailer, so it doesn't count."""
        out = self.run_hook(f"{CREDIT}\n\nMore text.", FAKE_VIEW=view("bot", "human"))
        self.assertIn("4242+human@", self.reason(out))

    def test_credit_for_another_login_is_still_missing(self) -> None:
        """A credit line for someone else doesn't satisfy a different author."""
        other = "Co-authored-by: Z <9+other@users.noreply.github.com>"
        out = self.run_hook(f"A body.\n\n{other}", FAKE_VIEW=view("bot", "human"))
        self.assertIn("4242+human@", self.reason(out))

    def test_pr_authors_own_commits_need_no_credit(self) -> None:
        """Commits by the PR's own author, in any letter case, add no line."""
        out = self.run_hook("A body.", FAKE_VIEW=view("Human", "human"))
        self.assertEqual((out, self.calls()), ("", [f"pr view 7 {VIEW_ARGS}"]))

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

    def test_failed_id_lookup_leaves_a_placeholder(self) -> None:
        """When the id can't be fetched the refusal still names the line, with `<id>`."""
        out = self.run_hook("A body.", FAKE_VIEW=view("bot", "human"), FAKE_API_FAILS="1")
        self.assertIn("<id>+human@users.noreply.github.com", self.reason(out))

    def test_failed_lookup_refuses_the_merge(self) -> None:
        """When `gh pr view` fails the credit can't be checked, so the merge is refused."""
        out = self.run_hook("A body.", FAKE_VIEW_FAILS="1")
        self.assertIn("Couldn't read the PR's authors", self.reason(out))

    def test_unreadable_lookup_refuses_the_merge(self) -> None:
        """Output that isn't the expected JSON is refused the same way."""
        out = self.run_hook("A body.", FAKE_VIEW="not json")
        self.assertIn("Couldn't read the PR's authors", self.reason(out))

    def test_lookup_of_the_wrong_shape_refuses_the_merge(self) -> None:
        """A login that isn't a string, or authors that aren't a list of objects, are refused."""
        shapes = (
            {"author": {"login": "bot"}, "commits": [{"authors": [{"login": 5, "name": "x"}]}]},
            {"author": {"login": "bot"}, "commits": [{"authors": "abc"}]},
            {"author": {"login": None}, "commits": []},
        )
        for shape in shapes:
            with self.subTest(shape=shape):
                out = self.run_hook("A body.", FAKE_VIEW=json.dumps(shape))
                self.assertIn("Couldn't read the PR's authors", self.reason(out))

    def test_message_and_credit_problems_are_reported_together(self) -> None:
        """A wrapping problem and a missing credit both appear in one refusal."""
        out = self.run_hook("word " * 20, FAKE_VIEW=view("bot", "human"))
        reason = self.reason(out)
        self.assertIn("over the 72-character wrap", reason)
        self.assertIn("4242+human@", reason)

    def test_a_flags_value_is_not_the_pr(self) -> None:
        """The values of `--match-head-commit` and `-A` stay out of the lookup's PR argument."""
        self.run_hook("A body.", "--match-head-commit abc1234 -A me@example.com", FAKE_VIEW=view("bot", "bot"))
        self.assertEqual(self.calls(), [f"pr view 7 {VIEW_ARGS}"])

    def test_repo_flag_reaches_the_lookup(self) -> None:
        """`-R owner/repo` is passed to `gh pr view`, so the PR read is that repo's."""
        self.run_hook("A body.", "-R owner/repo", FAKE_VIEW=view("bot", "bot"))
        self.assertEqual(self.calls(), [f"pr view 7 -R owner/repo {VIEW_ARGS}"])

    def test_no_selector_reads_the_current_branchs_pr(self) -> None:
        """With no PR named, `gh pr view` gets none and so reads the current branch's."""
        command = f"gh pr merge --squash --subject '{SUBJECT}' --body-file - <<'EOF'\nA body.\nEOF"
        self.run_command(command, FAKE_VIEW=view("bot", "bot"))
        self.assertEqual(self.calls(), [f"pr view {VIEW_ARGS}"])

    def test_a_body_without_a_subject_is_checked_for_credit(self) -> None:
        """An explicit body replaces GitHub's default one, so it needs its credit lines."""
        command = "gh pr merge 7 --squash --body-file - <<'EOF'\nA body.\nEOF"
        out = self.run_command(command, FAKE_VIEW=view("bot", "human"))
        self.assertIn("4242+human@", self.reason(out))

    def test_a_merge_giving_no_message_is_not_checked(self) -> None:
        """With neither subject nor body GitHub writes the message, and the hook makes no call."""
        self.assertEqual((self.run_command("gh pr merge 7 --squash"), self.calls()), ("", []))

    def test_a_repo_outside_the_kit_is_not_checked(self) -> None:
        """Away from the kit the hook makes no `gh` call at all."""
        command = f"gh pr merge 7 --squash --subject '{SUBJECT}' --body-file - <<'EOF'\nA body.\nEOF"
        out = self.run_command(command, cwd=self.tmp, FAKE_VIEW=view("bot", "human"))
        self.assertEqual((out, self.calls()), ("", []))


if __name__ == "__main__":
    unittest.main()
