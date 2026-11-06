# Decision records (ADRs)

An ADR records *why* a non-obvious design choice was made, and the alternatives rejected. The rule a reader must *follow* belongs in a convention doc.

## When to write one

Write one for a non-obvious approach a reader would ask "why this way?" about, or a choice whose rejected alternatives are worth keeping. Routine or self-evident decisions get none.

## Format

One file per decision in `docs/decisions/`, named `NNN-kebab-title.md` (zero-padded, sequential), titled `# NNN - Title`, with:

- `## Decision` - what was decided, stated plainly.
- `## Reason` - why, with alternatives rejected.
- `## Consequences` - what follows: trade-offs, constraints, follow-ups.

## Register

`docs/decisions/README.md` indexes every ADR:

<!-- markdownlint-disable MD057 -->

| # | Decision | Status |
| --- | --- | --- |
| 001 | [Short title](001-...md) | Accepted |

<!-- markdownlint-enable MD057 -->

One row per ADR. Status: `Proposed` under discussion, `Accepted` once adopted, `Superseded` when replaced.

## Superseding

When a later ADR changes an earlier one, set the old one's status to `Superseded` with a note at its foot pointing to the new one; the new ADR names what it replaces. The old text stays.

## Reversing a decision

Distinct from superseding: the evidence overturning an accepted ADR comes from *acting on it* (a migration designed, a spike built), and no later ADR replaces it because the question is the same.

Rewrite that ADR in place, original case intact, with a status line saying the reasoning below argues for a conclusion the ADR did not reach. Trimming it to fit the outcome makes the answer look always obvious, hides which parts survive the reversal, and strips the referents of the corrections the reversal makes to named claims.

Name the conditions for revisiting and what would *not* be one; the second heads off an argument already weighed. Where an ADR anticipates its own rejection and says what then, follow it: it had the fullest view of the question.
