---
name: pr
description: Draft and open a pull request for the current branch
argument-hint: "[short summary of the change, optional]"
---

# Open a pull request

Reaching this skill means opening the PR is approved (user typed `/pr`, caller asked and got a yes, or a change's stage reached its gate): open with no draft review; the closing report is where it gets corrected.

`$ARGUMENTS`, if given, is extra context for the draft. In this turn:

1. **Get the branch pushed.** Uncommitted work, unpushed branch, or still on the default branch: follow `skills/push/SKILL.md` first.
2. **Check for an existing PR:** `gh pr list --head <branch>`. One open: report its URL and stop.
3. **Run the repo's full local check**, as `KIT.md`'s "Linting and formatting" says.
4. **Audit `git diff <base>...HEAD` for what CI cannot see.** CI never reads prose, so doc drift merges as easily as code: docs teaching a pattern the branch changed, review-enforced conventions, a doc page the repo's guidance ties to a file the branch touched. Search the tree for the branch's name too: a sentence calling the work unmerged or in review turns false at the merge. Fix what turns up and push it.
5. **Draft title and body** from that diff, `git log <base>..HEAD` if you need the full change set, and `conventions/git.md`/`conventions/github.md`:
   - Title: `conventions/git.md`'s commit subject rules, at most 72 characters once `(#<PR>)` is appended (it becomes the squash subject). Breaking change: `!` plus a `BREAKING CHANGE:` body line saying what consumers must do. CI checks both.
   - Body: 1-3 bullet summary points plus a test plan checklist. A change's stage takes the body `conventions/specs.md` gives for one instead.
   - `Closes #X` for each issue merging finishes. Read `conventions/git.md`'s `Closes #X` rule first: confirm every number is an issue. No number in hand: no such line.
   - Both are published verbatim, every line written for a reader who never saw this conversation, saying what the change is. Notes to yourself and accounts of what was left out stay in the conversation.
6. **Open it:** `gh pr create` against the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), title and body verbatim; body via `--body-file` or heredoc, keeping formatting.
7. **Read the body back** (`gh pr view --json body`) as that reader. Catches lines that only answer your own reasoning; fix with `gh pr edit`, or, if it fails with "required scopes" (`read:org`), `gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@<file>`.
8. **Report** PR number and URL, and the title and body as opened. Where the repo's `CLAUDE.md` names reviews under `## Reviews` (or in the doc that heading points to), offer those the diff matches, each with its reason; one runs when the user asks.
