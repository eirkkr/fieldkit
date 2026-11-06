---
name: pr
description: Draft and open a pull request for the current branch
argument-hint: "[short summary of the change, optional]"
---

# Open a pull request

Reaching this skill means opening the PR is approved (the user typed `/pr`, the caller asked and got a yes, or a change's stage reached its gate), so it opens with no review of the draft; the closing report is where it gets corrected.

`$ARGUMENTS`, if given, is extra context for the draft. In this turn:

1. **Get the branch pushed.** With uncommitted work, an unpushed branch, or no branch yet because you're still on the default one, follow `skills/push/SKILL.md` first.
2. **Check for an existing PR:** `gh pr list --head <branch>`. If one is open, report its URL and stop - there is nothing to create.
3. **Run the repo's full local check**, as `KIT.md`'s "Linting and formatting" says.
4. **Audit `git diff <base>...HEAD` for what CI cannot see.** CI never reads prose, so doc drift merges as easily as code: docs teaching a pattern the branch changed, review-enforced conventions, a doc page the repo's guidance ties to a file the branch touched. Search the tree for the branch's name too: a sentence calling the work unmerged or in review turns false at the merge. Fix what turns up and push it.
5. **Draft the title and body** from that diff, `git log <base>..HEAD` if you need the branch's full change set, and `conventions/git.md`/`conventions/github.md`:
   - Title: `conventions/git.md`'s commit subject rules, and at most 72 characters once `(#<PR>)` is appended - it becomes the squash subject. A breaking change takes `!` and a `BREAKING CHANGE:` line in the body saying what consumers must do. CI checks both.
   - Body: 1-3 bullet summary points plus a test plan checklist. A stage of a change takes the body `conventions/specs.md` gives for one instead.
   - `Closes #X` for each issue that merging finishes. Read `conventions/git.md`'s `Closes #X` rule before writing one: every number is confirmed an issue first. With no number in hand, the body has no such line.
   - Both are published verbatim, every line written for a reader who never saw this conversation and saying what the change is. Notes to yourself and accounts of what was left out stay in the conversation.
6. **Open it:** `gh pr create` against the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), passing the title and body verbatim - the body through `--body-file` or a heredoc, so it keeps its formatting.
7. **Read the body back** (`gh pr view --json body`) as that reader. A line that only answers your own reasoning is what this catches; fix it with `gh pr edit`.
8. **Report** the PR number and URL, and the title and body as opened. Where the repo's `CLAUDE.md` names reviews under `## Reviews`, or in the doc that heading points to, offer the ones the diff matches, each with its reason; one runs when the user asks.
