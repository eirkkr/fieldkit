---
name: merge
description: Merge the current branch's pull request via squash merge
---

# Merge a pull request

Reaching this skill means merging is approved for the branch as it stands - the user typed `/merge`, or the caller asked and got a yes - once every check has finished and passed. Note `git rev-parse HEAD` first: that commit is what was approved. Opening the PR and pushing the commits already on the branch are covered. A push that adds a commit is not: it voids the approval, so stop, report what the new commit holds, and ask again. That holds for a fix to a failing check, for anything steps 1 or 3 push, and for a push from anyone else. In this turn:

1. **Get a PR open.** With no open PR for this branch, follow `skills/pr/SKILL.md` first. If that pushes a new commit, such as an audit fix, stop as above.
2. **Check it can merge:** `gh pr view --json number,title,state,mergeable,statusCheckRollup,baseRefName,headRefName,url`. If it's not open or has conflicts, stop and report what's blocking it - waiting fixes neither. Checks still running are waited out in step 5.
3. **Rewrite claims the merge falsifies.** Run `git grep -n -e '#<N>' -e 'pull/<N>' -e '<branch>'`. A sentence calling the PR or branch open, unmerged or in review turns false at the merge: rewrite it on the branch and push it, which voids the approval, so report it and ask again.
4. **Draft the squash subject and body**, summarising the whole change rather than concatenating its commits. Start from context already in hand plus `git log <base>..<branch>` for every commit message, and read `git diff <base>...<branch>` only when those don't add up to a clear picture.
   - The message follows `conventions/git.md`'s Commits rules, with `(#<PR>)` ending the subject and counting toward its 72. A `!` title's `BREAKING CHANGE:` line comes over from the PR body. The kit's merge-message hook refuses a merge that breaks these, saying what to fix.
   - `Closes #X` lines: read `conventions/git.md`'s Squash-merge rule before writing one. It names the two sources a number may come from and the check that it is an issue. With no number, there is no such line.
5. **Wait for checks still running:** `gh pr checks --watch --fail-fast --interval 15`, with a Bash timeout up to the 600000ms maximum. Merge only once every check has finished and passed. If one fails, stop and report which; a fix is a new commit, so it needs a fresh approval. If the wait times out first, stop and report that CI is still running; `/merge` can be run again later.
6. **Push** the branch if commits that were there at approval aren't on the remote yet.
7. **Merge:** `gh pr merge <PR> --squash --match-head-commit=<approved sha>` with the drafted subject and body - the body through `--body-file -` and a heredoc, so it keeps its line breaks. GitHub refuses the merge if the head has moved; the `=` keeps the merge-message hook from reading the SHA as a PR number.
8. **Clean up locally:** switch to the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), force-delete the merged branch (`git branch -D <branch>` - a squash merge isn't recognised as merged by plain `-d`), and `git pull --prune`.
9. **Report** the PR number and URL, and that it merged and was cleaned up - or what is still blocking it.
