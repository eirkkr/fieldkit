# 057 - A plan priced to decide keeps its stages in sub-issues

## Decision

A plan the reviewer asks for to find out whether to do a change - a plan priced to decide, "Planning to decide" in [specs.md](../../conventions/specs.md) - gets its stage sub-issues when it is published, each holding that stage's steps. Every other plan still gets them on approval. If the answer is no, the stage sub-issues are closed as not planned with the change, and stay as the record of what each stage would have cost.

This amends [054](054-a-change-is-an-issue.md), which put a priced plan's steps into the first build notes and created no stage issue before approval.

## Reason

The build notes are capped at about 150 lines, so that notes which outgrow the cap show a change that should have been two. A plan priced to decide is the one kind that is meant to be big: it exists because a decision is large and hard to undo. The first one to be moved onto this workflow from an older format - a consumer's database migration, costed and turned down - holds 19 stages in a 212-line task list, beside a 181-line design. In the notes it would break the cap by itself, and the cap would stop meaning anything.

Sub-issues are already where a stage's steps live once it starts, so a reader of a turned-down plan finds each stage's price where a stage's steps always are. A stage's issue also has room for its own discussion, and for a correction found while pricing a later stage.

Rejected:

- **Raising the cap for a priced plan.** Keeps one place to read, but a cap with an exception for the largest case does not cap anything, and the next agent has to read every stage to find one.
- **One comment per stage on the change's issue.** Nothing to create or close, but stages lose their titles, their blocking links and their place in the sub-issue list, and become hard to tell apart from review findings in a long thread.
- **Keeping a priced plan as files in the repository, as an evaluation.** Holds any size, and a clone carries it. But it is the in-repository record 054 retired, and it would be the one kind of change whose history lives somewhere other than its issue.

## Consequences

- A priced plan's stage issues are created without a further ask when it is published, as any plan's are on approval. `KIT.md`'s approval rules say so.
- A priced plan that is approved already has its stages. `change-plan` creates none on approval, and `change-stage` corrects the existing steps against the repository when a stage starts, instead of writing them, saying what it changed in a comment.
- A turned-down plan closes more issues: the change and each of its stages, all as not planned.
- A consumer's older evaluation folder can move onto this: a change issue for the plan, a sub-issue per stage with its steps, all closed as not planned, and the ADR that turned it down linking the change.
