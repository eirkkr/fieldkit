# 047 - Enforce commit messages at commit, merge and PR

## Decision

`conventions/git.md`'s commit rules become strict, with no targets:

- Subject: `type: description`, type one of `feat`, `fix`, `docs`, `refactor`,
  `test`, `chore` - no scope, no `!`, no other types - description starting
  lowercase, no trailing period, at most 72 characters.
- Body: after a blank line, every line at most 72 characters, except a line
  that is one unbreakable word (a URL or a path), optionally after a list
  marker or a `[1]:` label.
- A squash subject ends `(#N)` for its PR, and the 72 includes it, so a PR
  title has 72 minus the suffix - 65 for a three-digit PR.

"Aim for 50 characters" is dropped from `git.md`.

The rules live as constants in `hooks/conventions.py`, with the branch-name
rules from ADR 046 moved in beside them. Three checks import it:

- **`hooks/commit-msg`**, a git hook `scripts/enable-hooks.sh` now installs
  with `pre-commit`. It refuses any commit breaking the rules, except messages
  git writes itself: merges, reverts, `fixup!`, `squash!` and `amend!`.
- **`hooks/pretooluse-merge-message.py`**, a `PreToolUse` hook on `Bash`,
  registered by `just install`. It checks the message Claude passes to
  `gh pr merge --subject ... --body-file -`, including that the suffix matches
  the PR in the command. With no `--subject`, GitHub builds the subject from
  the PR title, so the merge is let through for CI's check to cover.
- **A `pr-title` job** in the reusable workflow, now
  `.github/workflows/pr-conventions.yml` (renamed from `branch-name.yml`),
  checking the PR title plus its suffix. The workflow re-runs on `edited`, so
  a retitled PR is checked again. `scripts/enable-pr-checks.sh` replaces
  `enable-branch-check.sh` and swaps an old caller for the new one.

The shared shell parsing now cuts heredoc bodies out before tokenising, which
both `PreToolUse` hooks rely on.

## Reason

The rules were instruction-only, and slipped the way the branch names did.
Across all 85 commits on this repo's default branch, 139 body lines run past
72 without being a URL or path, and so do 236 across the last 300 of one
consumer repo's. Several of this repo's came from squash bodies an agent
drafted.

**Strict limits, and why 72 for both.** Looked at as sources rather than
folklore:

- Git's own `git commit` documentation suggests "no more than 50 characters"
  for the first line, "though not required".
- The 2008 note the "50/72 rule" comes from says "shoot for about 50
  characters (though this isn't a hard maximum)" and wraps the body "to about
  72".
- The Linux kernel's patch guide caps the summary at "70-75 characters" and
  wraps at 75.
- GitHub cuts a subject longer than 72 on its commit pages.
- commitlint's widely used conventional config errors at 100 for both.

A limit here is either enforced or absent. 50 is soft in every source that
defines it, and enforcing it leaves about 43 characters for a PR title; 100
targets no display. 72 is the one subject length with a mechanical reason -
GitHub's cutoff - and the body's 72 has its own: `git log` indents the body by
4 and doesn't wrap it, so 72 keeps it inside 80 columns. The layout width the
repo code page truncates to varies with the window, so it can't anchor a
number.

**The unbreakable-line exemption.** A line that can be wrapped has a space in
it. One that doesn't - a URL, a path - can't be, so refusing it would demand
the impossible. Written as a pattern, the exemption can refuse a long line
with spaces and nothing else.

**Where each check sits.** The kit squash-merges, so a branch's own commits
never reach the default branch; the squash commit is the lasting one, and its
message is set at merge time. Each check covers a different writer of it:

- CI checks the PR title, which is what GitHub uses for the subject on a UI
  merge - and CI can't see a message chosen at the moment of merging.
- The merge hook covers Claude's merges, which pass a custom subject and
  body. It is the only point where the `(#N)` suffix can be checked, since
  GitHub omits it from a custom subject.
- The `commit-msg` hook covers branch commits, which show in review even
  though the squash replaces them. Git hands it the whole message as a file,
  so it needs no parsing of `-m` or heredoc text, and it catches humans and
  Claude alike.

**The type list stays at six.** Conventional Commits itself defines only
`feat` and `fix`; the rest is convention layered on it. `ci` and `style` are
common in that layer, and an agent reached for both on this repo's own
history - which is the drift a closed list exists to stop, not a reason to
widen it.

**One module for every rule.** Four checks now read naming rules. Keeping
them in one imported module keeps ADR 046's one-copy property as the
readers multiply; the hooks already sit next to it, and git resolves the
`commit-msg` symlink to find it.

Alternatives rejected:

- **A `PreToolUse` hook on `git commit`.** It would have to recover the
  message from the command text, heredocs included. `commit-msg` gets it from
  git directly, and catches humans too.
- **Checking branch commits in CI.** They are squashed away; failing a PR on
  a message that never reaches the default branch is friction for no lasting
  gain. The `commit-msg` hook covers them locally.
- **A separate reusable workflow for titles.** A second file consumers call,
  when one workflow with two jobs covers both with one caller.

## Consequences

- Squash merges through GitHub's UI keep `(#N)` only when the repo's squash
  default is the PR title. The default "commit or PR title" uses a lone
  commit's subject instead, which CI never checked. That setting is per repo
  and outside the kit's reach.
- A UI merge's body comes from the repo's squash-message setting and is not
  checked by anything: GitHub's PR-body default is Markdown, not wrapped at
  72. Claude's merges are checked; a human's UI merge relies on the setting.
- The `commit-msg` hook is opt-in per clone, like `pre-commit`. A clone
  without it only meets the rules at the PR.
- Renaming the workflow breaks a consumer's old caller until
  `enable-pr-checks.sh` is re-run there: GitHub can't find
  `branch-name.yml@main` any more. Callers can't pin a version to ride this
  out (see the kit's issue on release tags).
- `git commit --no-verify` bypasses the `commit-msg` hook, as it does
  `pre-commit`, and is left out of its output for the same reason.
- The branch hook no longer has a `--name` mode; `conventions.py branch
  <name>` replaces it, and `check-branch-name.sh` calls that.
