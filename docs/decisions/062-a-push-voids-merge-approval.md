# 062 - A push voids merge approval

## Decision

Approval to merge covers one head: the short SHA the agent names when it asks, or the current head after a typed `/merge`. A later push that adds or rewrites a commit voids it: a fix to a failing check, a rebase, an edit the merge itself makes, a commit from anyone. The agent stops, reports what changed, and asks again. A fresh yes or `/merge` approves the new head.

The one exception is the commit a stage gate's own approval step adds: the decision record, and for a staged change the **Reviewed at** line and the tick. The reviewer's yes commissions it, the gate's instructions name it, and it holds nothing else, so the approved sha is the head it leaves. The exception is in `skills/change-stage/GATE.md` and the review-gated schema, not left to the agent's judgement of a push.

`skills/merge/SKILL.md` takes the approved sha in full, stops where its own steps would add or rewrite a commit, checks the PR's `headRefOid` against it, and passes `--match-head-commit=<approved sha>` to `gh pr merge`, so GitHub refuses a merge whose head has moved. Pushing commits up to the approved sha stays covered. The flag is written with `=`: given a space, `hooks/pretooluse-merge-message.py` reads an all-digit SHA as the PR number. `KIT.md` states the rule in the Merging row and in a bullet of its own.

This amends [030](030-ungate-merge.md), [031](031-regate-pr-and-merge-invocation.md) and [032](032-merge-waits-out-pending-ci.md), which conditioned a merge on CI alone or on the invocation, and the "pushing along the way" that the skill said approval covered.

## Reason

An approval is a judgement about a particular tree. In a consumer repo a user said to merge, CI could not run, the local run of everything CI runs failed on a test the PR had added, and the agent fixed it, pushed and merged in the same turn. The merged tree held a commit the user had never seen. Every rule as written allowed it: the approval was given, the checks passed on the final head, and nothing said that new commits mattered.

The condition is the head, not the kind of change. A rule with exceptions for docs-only or test-only pushes asks the agent to judge, in the moment, that its own change is harmless, which is the judgement the approval was meant to reserve to the user. A re-ask costs one turn.

Rejected:

- **Void only pushes that change code.** The agent would decide what counts as code, and a comment or a test is part of what was approved.
- **No exception for the gate's closing commit.** A gate would ask twice, or never merge: the commit it writes after the yes would void the yes. The exception is narrow and named, so it is not a judgement the agent makes of its own change.
- **Check the head in the skill alone.** `--match-head-commit` makes GitHub enforce it too, which covers a push from anyone and the gap between the skill's last check and the merge call, the race [030](030-ungate-merge.md) accepted.
- **State the rule in `conventions/git.md`.** [050](050-approval-rules-live-in-kit-md.md) keeps who approves out of the conventions docs.

## Consequences

- A merge that has to fix something first takes a second approval. The common path, where nothing is pushed after the approval, is unchanged.
- Any other commit a merge makes on the way, step 3's rewrite of a sentence calling the PR unmerged, or an audit fix the `pr` skill pushes when `/merge` opens the PR, ends in a question, not a merge. The `pr` skill makes that audit before the PR is opened, so it is mostly the first-run case.
- A stage gate's closing commit does not void the approval, and the merge passes the head it leaves. A gate that wrote anything else after the yes would.
- `KIT.md` grows by a bullet; the always-loaded budget in [060](060-budget-the-always-loaded-context.md) still holds.
- A consumer that documents its own route around a failed CI run, as one does for billing refusals, should say that a fix made along the way voids the approval too.
