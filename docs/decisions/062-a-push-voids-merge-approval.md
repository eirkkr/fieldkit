# 062 - A push voids merge approval

## Decision

Approval to merge covers the head the branch had when it was given. Any push after that voids it: a fix to a failing check, a rebase, an edit the merge makes itself, a commit from anyone. The agent stops, reports what changed, and asks again. A `/merge` typed afresh is a fresh approval.

`skills/merge/SKILL.md` notes `git rev-parse HEAD` when it starts, stops where its own steps would push a new commit, and passes `--match-head-commit=<sha>` to `gh pr merge`, so GitHub refuses a merge whose head has moved. Pushing commits that were on the branch at approval stays covered. `KIT.md` states the rule in the Merging row and in the bullet on CI.

This amends [030](030-ungate-merge.md) and [032](032-merge-waits-out-pending-ci.md), which conditioned a merge on CI alone, and the "pushing along the way" that the skill said approval covered.

## Reason

An approval is a judgement about a particular tree. In a consumer repo a user said to merge, CI could not run, the local run of everything CI runs failed on a test the PR had added, and the agent fixed it, pushed and merged in the same turn. The merged tree held a commit the user had never seen. Every rule as written allowed it: the approval was given, the checks passed on the final head, and nothing said that new commits mattered.

The condition is the head, not the kind of change. A rule with exceptions for docs-only or test-only pushes asks the agent to judge, in the moment, that its own change is harmless, which is the judgement the approval was meant to reserve to the user. A re-ask costs one turn.

Rejected:

- **Void only pushes that change code.** The agent would decide what counts as code, and a comment or a test is part of what was approved.
- **Check the head in the skill alone.** `--match-head-commit` makes GitHub enforce it too, which covers a push from anyone and the gap between the skill's last check and the merge call, the race [030](030-ungate-merge.md) accepted.
- **State the rule in `conventions/git.md`.** [050](050-approval-rules-live-in-kit-md.md) keeps who approves out of the conventions docs.

## Consequences

- A merge that has to fix something first takes a second approval. The common path, where nothing is pushed after the approval, is unchanged.
- Step 3 of the merge skill, which rewrites a sentence calling the PR unmerged, now ends in a question, not a merge. The `pr` skill's audit already makes that rewrite before the PR is opened, so it is the exception.
- A consumer that documents its own route around a failed CI run, as one does for billing refusals, should say that a fix made along the way voids the approval too.
