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

Distinct from superseding, and worth its own handling: an ADR is accepted,
and the evidence that overturns it is produced *by acting on it* - a
migration designed, a spike built, a rollout begun. There is no later ADR
replacing it, because the question it asked is the same question.

Rewrite that ADR in place, and keep the original case intact rather than
trimming it to fit the outcome. Add a section recording what changed and
why, and say in the status line that the reasoning below argues for a
conclusion the ADR did not reach. Three reasons the case stays:

- A decision reversed on evidence is only legible next to the case it
  reversed. Trimmed, it reads as though the answer was always obvious,
  which teaches nobody anything.
- Parts of it usually survive the reversal untouched, and a reader needs
  to know which. "Nothing had ever chosen this, and that is worth fixing"
  can be the reason the question was asked and remain true whichever way
  it resolves.
- The reversal's own argument tends to be *specific corrections to named
  claims* in the original. Delete the claims and the corrections lose
  their referents.

Name the conditions under which to revisit, in the ADR. That is what
stops a settled question decaying into one nobody looked at again, and it
is more useful than a status: a reader who meets one of the conditions
knows the decision is theirs to reopen. Say what would *not* be a reason,
too - it is as informative, and it heads off the argument that was
already weighed.

Where an ADR anticipates its own rejection and says what should happen
then, follow it. That instruction was written with the fullest view of
the question anyone has had.
