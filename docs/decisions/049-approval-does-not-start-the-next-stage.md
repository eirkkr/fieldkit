# 049 - Approving a gate does not start the next stage

## Decision

Approving a stage's review gate records the approved commit, ticks the gate
and merges the stage's PR. It starts nothing. The next stage begins when the
human asks for it: by invoking the apply skill again, or by saying so, in
the approval itself ("approved, carry on with stage 3") or later.

The rule is stated in the `review-gated` schema's `apply` instruction, in
the gate task its `tasks` instruction and template write, in the kit's
overlay on the `openspec-apply-change` skill, and in `conventions/specs.md`.

## Reason

[ADR 034](034-review-gated-openspec-schema.md) made a gate a hard stop, and
[ADR 041](041-stage-is-the-merge-unit.md) made approval merge the stage.
Neither said what happens next, but the instructions written from them did.
The `apply` instruction's approval paragraph ended "Then start the next
stage on a fresh branch", the skill overlay's "The next stage then starts on
a fresh branch", and every gate task read "do not begin stage 3, until the
reviewer approves".

The first two were written to say *where* the next stage branches from, and
the third what blocks it. An agent reads all three as *when* to begin. In a
consumer repo a reviewer wrote "review complete, i approve"; the agent
merged the stage and cut the next one's branch in the same turn. The
reviewer reported it as a repeat.

Starting unasked costs more than tokens:

- **The gap between stages is where the plan changes.** A review note ends
  with the stage's impact on later stages, and the reviewer who has just
  read it may want to revise, reorder or drop the next one. Work begun on
  the old plan has to be undone first.
- **Approval says the stage is good, not that now is the time for the
  next.** That depends on things the agent cannot see, such as what else is
  queued.
- **The human sets the pace.** That is ADR 034's point, and an agent
  rolling from one stage into the next takes it back.

**Requiring a separate invocation every time was rejected.** It is the
simplest rule to state, but it costs the reviewer two messages where one
says everything. The failure was the agent inferring a request, not the
human making one too easily.

**Leaving the wording and relying on judgement was rejected.** The agent was
following its instructions. A rule that depends on an instruction being read
against its plain meaning does not hold across sessions.

## Consequences

- The reviewer makes one more decision per stage, usually a few words in
  the approval.
- The rule stands in five files: the schema, its tasks template, the
  overlay, the vendored skill that ends with the overlay, and
  `conventions/specs.md`. `just check-overlays` keeps the overlay and the
  skill together; nothing checks the others.
- A `tasks.md` written before this change keeps the old sentence in its
  gates. It needs no rewrite: the `apply` instruction and the skill are read
  on every run.
- A consumer reaches the schema and the skill through symlinks, so it
  follows the rule as soon as its kit checkout has this change.
