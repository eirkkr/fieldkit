# 059 - Small findings are fixed in place

## Decision

A finding unrelated to a branch's change is fixed on that branch when the fix costs less than filing an issue, or only slightly more. The fix is its own commit, and the PR description names it. Claude makes it act-then-show, like any other commit on the branch. A larger finding becomes an issue, as before. On a change's stage PR, a fix in place is allowed only in a file the stage already touches. Its commit has no step number, and the PR body's **Changed from the plan** names it. The rules are in `KIT.md`, `conventions/github.md`, `conventions/specs.md` ("Building a stage") and the `change-stage` skill.

## Reason

The kit used to send every out-of-scope finding to an issue, however small. An issue has costs of its own: a body that stands alone ([records.md](../../conventions/records.md)), a duplicate search, then a later branch, PR, review and merge, with the context rebuilt by whoever picks it up. For a one-line fix, all of that costs more than the fix. A separate commit keeps the fix separable in history and review, and naming it in the PR description shows the reviewer it is there on purpose. "Spans modules", the old line between fixing a convention violation and filing it, is now treated as a sign of size, not the rule itself.

Stage PRs are narrower because a stage is reviewed against its steps. An unplanned fix in a file the stage doesn't touch leaves the reviewer checking work that nothing in the plan accounts for. A fix in a file the stage touches is already in front of them.

Rejected:

- **The same rule on stage PRs as on ordinary ones.** It keeps one rule, but adds unplanned files to a review that is scoped by its steps.
- **No fixes in place on stage PRs.** This keeps today's rule there. It throws away cheap fixes in files the reviewer is already reading.
- **Asking before a fix in place.** The fix is visible in its own commit and in the PR description, and can be taken out on request. A question would cost about what the issue did.

## Consequences

- PRs carry the occasional unrelated commit. The PR description is what tells a reviewer which commits those are.
- "Costs less than filing an issue, or only slightly more" is a judgement, not a measure. A fix that grows while it is being made stops being small, and it becomes an issue.
