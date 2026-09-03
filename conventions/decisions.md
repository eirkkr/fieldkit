# Decision records (ADRs)

Record non-obvious design decisions as lightweight ADRs so the rationale -
and the alternatives rejected - survive. An ADR explains *why* a choice was
made; the rule a reader must *follow* belongs in a convention doc, not here.

## When to write one

- A non-obvious approach where a reader would reasonably ask "why this way?"
- A choice with alternatives worth recording as rejected.
- Not for routine or self-evident decisions.

## Format

One file per decision in `docs/decisions/`, named `NNN-kebab-title.md`
(zero-padded, sequential). Title `# NNN - Title`, then:

- `## Decision` - what was decided, stated plainly.
- `## Reason` - why, including alternatives considered and rejected.
- `## Consequences` - what follows: trade-offs, constraints, follow-ups.

## Register

`docs/decisions/README.md` indexes every ADR:

<!-- markdownlint-disable MD057 -->

| #   | Decision                 | Status   |
| --- | ------------------------ | -------- |
| 001 | [Short title](001-...md) | Accepted |

<!-- markdownlint-enable MD057 -->

Add a row per ADR. Status is `Accepted` once adopted (`Proposed` while under
discussion, `Superseded` when replaced).

## Superseding

Don't rewrite history. When a later ADR changes an earlier one, set the old
one's status to `Superseded` with a note at its foot pointing to the new one;
the new ADR references what it replaces.

## Reversing a decision

Distinct from superseding: an ADR is accepted, and the evidence that
overturns it comes from *acting on it* - a migration designed, a spike
built. No later ADR replaces it, because the question is the same one.

Rewrite that ADR in place and keep the original case intact rather than
trimming it to fit the outcome, with a status line saying the reasoning
below argues for a conclusion the ADR did not reach. Trimmed, it reads
as though the answer was always obvious; parts of it usually survive the
reversal and a reader needs to know which; and the reversal's argument
is typically a set of corrections to named claims, which lose their
referents once the claims are gone.

Name the conditions for revisiting, and what would *not* be one - the
second is as informative, and heads off an argument already weighed.
Where an ADR anticipates its own rejection and says what should happen
then, follow it: that instruction had the fullest view of the question.
