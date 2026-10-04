# 052 - Divide what a change writes by its reader

## Decision

Everything a review-gated change writes has one of two readers, and the schema now says which.

- **The reviewer reads briefs.** Two kinds: the plan brief that opens `tasks.md`, read to approve the plan, and the brief that opens each stage's review note, read to approve the stage. A brief holds what the reviewer has to decide and where to look, to a length budget - one screen for the plan, about ten lines for a stage.
- **The implementing agent reads everything else.** `proposal.md`, the specs, `design.md`, the tasks, and each note's record. Complete, sized for a reader starting with no context, and never required reading for the reviewer.

The review note's items are divided rather than cut. The brief carries the stage in a sentence, the PR's file view with its checks, what to look at closely, whether the plan held, and one thing to try by hand. The record carries the terminal diff and the commit walk, `Change based at`, what changed, the commands that verify it, what is not done yet, and `Reviewed at`. Each item lives in one part: the brief is not a summary of the record.

Three rules hold the split up:

- **The reply shows the brief only.** The record is in `tasks.md` for whoever wants it.
- **An empty item is said, not dropped.** A stage with no departure and no impact on later stages writes "Plan held" in one line; a final review with nothing wrong writes "Findings: none". The exception is the manual step, which is left out when there is none.
- **The budget gives way to one thing.** Departures from the plan and impact on later stages take a line each however many there are.

The final review follows the same rule: its lists - each requirement and where the code meets it, each issue re-read - go in the record, and the brief carries only what was found wrong or corrected.

This amends [034](034-review-gated-openspec-schema.md), which specified the note as one list, and builds on [041](041-stage-is-the-merge-unit.md).

## Reason

The reviewer reported not reading most of what a change produced, at the gates above all. The note had grown to eight items, one of them a link for every commit on the branch, and all eight were shown in the reply as well as written to `tasks.md`. Before the build there were four artifacts, with tasks sized for the least-skilled implementer.

None of that text was wrong, and most of it was not for the reviewer. A stage is built by an agent that starts with no context, and what it needs from the stage before it - what changed, how to verify it, what was left for later, which commit was approved - is exactly the detail a reviewer skims past. Written as one list, the two audiences cost each other: the reviewer had to read everything to find the lines that needed a decision, and those sat at positions three, five and seven of eight.

A review that is nominally of everything and actually of nothing is worse than one that is openly of a summary, because nobody can tell which parts were read. 034's own argument is that a gate has to be cheap or it becomes a rubber stamp; the note had become the expensive part of the gate.

**Making everything shorter was rejected.** It removes the detail the next agent depends on, and it still leaves the reviewer sorting their lines from the agent's.

**A separate `brief.md` artifact was rejected** for the plan brief. A brief has to be written last, so it would have to be what `apply` requires - the propose skill stops generating at the artifacts `apply` requires - and that would block every change already in flight until one was written for a plan already approved. A second file also drifts: a gate that changes the plan corrects `tasks.md` and `design.md`, and a brief elsewhere would be missed. At the top of `tasks.md` it sits in the file the gates already correct and the reviewer already opens, and the checkbox parser ignores it.

**Dropping empty items was rejected.** It is the cheapest way to shorten a brief, and it makes "nothing to report" indistinguishable from "did not check" on the two items where that difference is the point of the gate.

**Putting "not done yet" in the brief was considered.** 034 put it in the note so the reviewer would not report a planned gap as a defect. It moved to the record anyway: it is a list the reviewer needs only when they are about to raise something, and the agent answering them has it.

## Consequences

- The reviewer approves from text written by the agent that wrote the detail it stands for. A brief that misreports the plan or the stage is not caught by reading the brief. "Least sure of" and "Look closely at" are the guard - they exist to send the reviewer into the detail where it matters - and both instructions say never to leave them out.
- A reviewer who reads only the brief may report a gap that a later stage covers. The record answers it; the cost is a round trip.
- The commit walk is one click further away, in the record rather than at the top of the note. Nothing about it changed.
- The plan brief is one more thing a gate must keep true when the plan changes. The stage brief's plan item says so.
- A `tasks.md` written before this change has no plan brief and its closed gates carry single-list notes. Neither needs a rewrite: the `apply` instruction is read on every run, so the next gate writes the new form.
- The rule stands in the schema's `tasks` and `apply` instructions, its tasks template, the overlay on `openspec-apply-change`, the vendored skill that ends with it, and `conventions/specs.md`.

> [054](054-a-change-is-an-issue.md) keeps this division and moves both halves out of `tasks.md`: the reviewer's briefs are the change's issue body and each stage's PR body, and what the implementing agent reads is the build notes, a comment on the change's issue. "Look closely at" is dropped from the stage brief; "least sure of" stays in the plan's.
