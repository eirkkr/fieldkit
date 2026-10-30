---
name: merge
description: Merge the current branch's pull request via squash merge
---

# Merge a pull request

Reaching this skill means merging is approved for one head: the user typed `/merge`, or the caller asked and got a yes. That head is the SHA the caller named, else `git rev-parse HEAD` now; expand it with `git rev-parse <sha>^{commit}` and call it the approved sha. Any push that adds or rewrites a commit, or a moved head (step 2), voids the approval: make a fix and push it only where a step says to, then stop, report what changed, and ask again. After the new yes, the new head is the approved sha; carry on from step 2 (a fresh `/merge` starts at step 1). The one exception is this PR's gate approval commits, which `skills/change-stage/GATE.md` lists - the decision record, the **Reviewed at** line and the tick, nothing else, and not a fix the reviewer asked for. The approved sha is the head they leave. In this turn:

1. **Get a PR open.** With no open PR for this branch, follow `skills/pr/SKILL.md` first.
2. **Check it can merge:** `gh pr view --json number,title,state,mergeable,statusCheckRollup,baseRefName,headRefName,headRefOid,url`. If it's not open or has conflicts, stop and report what's blocking it - waiting fixes neither. After `git fetch`, a `headRefOid` that is not an ancestor of the approved sha (`git merge-base --is-ancestor <headRefOid> <approved sha>` fails) means the head moved: stop as above. One behind it is fine; step 6 pushes the difference. Checks still running are waited out in step 5.
3. **Rewrite claims the merge falsifies.** Run `git grep -n -e '#<N>' -e 'pull/<N>' -e '<branch>'`. A sentence calling the PR or branch open, unmerged or in review turns false at the merge: rewrite it on the branch and push it. Then stop and ask again, as above.
4. **Draft the squash subject and body**, summarising the whole change rather than concatenating its commits. Start from context already in hand plus `git log <base>..<branch>` for every commit message, and read `git diff <base>...<branch>` only when those don't add up to a clear picture.
   - The message follows `conventions/git.md`'s Commits rules, with `(#<PR>)` ending the subject and counting toward its 72. A `!` title's `BREAKING CHANGE:` line comes over from the PR body. The kit's merge-message hook refuses a merge that breaks these, saying what to fix.
   - `Closes #X` lines: read `conventions/git.md`'s Squash-merge rule before writing one. It names the two sources a number may come from and the check that it is an issue. With no number, there is no such line.
5. **Wait for checks still running:** `gh pr checks --watch --fail-fast --interval 15`, with a Bash timeout up to the 600000ms maximum. Merge only once every check has finished and passed. If one fails, stop and report which; fixing it is a new commit, so ask again as above. If the wait times out first, stop and report that CI is still running; `/merge` can be run again later.
6. **Push** only up to the approved sha, if the remote lacks commits up to it: `git push origin <approved sha>:refs/heads/<headRefName>`. If local HEAD is ahead of the approved sha, stop as above.
7. **Merge:** `gh pr merge <PR> --squash --match-head-commit=<approved sha>` with the drafted subject and body - the body through `--body-file -` and a heredoc, so it keeps its line breaks. GitHub refuses the merge if the head has moved: stop as above. Write the flag with `=`: given a space, the merge-message hook reads an all-digit SHA as the PR number.
8. **Clean up locally:** switch to the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), force-delete the merged branch (`git branch -D <branch>` - a squash merge isn't recognised as merged by plain `-d`), and `git pull --prune`.
9. **Report** the PR number and URL, and that it merged and was cleaned up - or what is still blocking it.
