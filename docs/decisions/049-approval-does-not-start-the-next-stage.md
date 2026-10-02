# 049 - Approving a gate does not start the next stage

## Decision

Approving a stage's review gate closes that stage: the approved commit is
recorded, the gate is ticked, and the stage's PR merges. It starts nothing.
The next stage begins only when the human asks for it - by invoking the
apply skill again, or by saying so.

The request may come in the same message as the approval ("approved, carry
on with stage 3"). An approval that does not mention the next stage is not a
request for it.

The rule is stated in the `review-gated` schema's `apply` instruction, in
the kit's overlay on the `openspec-apply-change` skill, and in
`conventions/specs.md`.

## Reason

[ADR 034](034-review-gated-openspec-schema.md) made a gate a hard stop, and
[ADR 041](041-stage-is-the-merge-unit.md) made approval merge the stage.
Neither said what happens next, and the instructions written from them did:
the schema's `apply` instruction ended its approval paragraph with "Then
start the next stage on a fresh branch cut from the default branch", and the
skill overlay with "The next stage then starts on a fresh branch".

Those sentences were written to say *where* the next stage branches from. An
agent reads them as *when*. In a consumer repo, a reviewer wrote "review
complete, i approve"; the agent closed the gate, merged, and in the same
turn cut the next stage's branch and began reading for it, before being
stopped. The reviewer reported it as a repeat. The agent was following the
text.

Starting unasked costs more than the tokens:

- **The gap between stages is where the plan changes.** Every review note
  ends with the stage's impact on the stages after it. A reviewer who has
  just read that may want to revise the next stage, reorder it, or drop it.
  Work already begun on the old plan has to be noticed and undone first.
- **Approval is evidence about what was read.** It says the stage is good.
  It says nothing about whether now is the time for the next one, which
  depends on things the agent cannot see: what else is queued, whether the
  reviewer is about to stop for the day.
- **A stage is the largest unit the reviewer agreed to.** ADR 034's point
  is that the human sets the pace. An agent that rolls from one stage into
  the next has taken that back, one approval at a time.

**Requiring a separate invocation every time was considered and rejected.**
It is the simplest rule to state - the next stage starts only on a new
`/openspec-apply-change` - but it makes the reviewer type two messages where
one says everything. "Approved, carry on" is as explicit as a request gets.
The failure was the agent inferring a request, not the human making one too
easily, so the rule is aimed at the inference.

**Leaving the wording and relying on the agent's judgement was rejected.**
The sentence is an instruction, and following it is what the agent is for.
A rule that depends on an instruction being read against its plain meaning
does not hold across sessions.

## Consequences

- A change costs the reviewer one more decision per stage, usually a few
  words in the approval. That is the point of it.
- A session that ends on an approval ends with the stage merged and the
  default branch checked out. Nothing is left half-begun.
- The same rule now stands in four files: the schema, the overlay, the
  vendored skill that ends with the overlay, and `conventions/specs.md`.
  `just check-overlays` keeps the middle two together; nothing checks the
  schema against them, as before.
- A consumer reaches the schema and the skill through symlinks into the
  kit, so it follows the rule as soon as its kit checkout has this change.
  Nothing has to be re-run.
