# 020 - Fold workflow.md into CLAUDE.md; restate act-then-show once

## Decision

`conventions/workflow.md` is deleted; its content moves directly into
`CLAUDE.md`'s "Load Always" section. The act-then-show statement, which had
drifted into two separate, overlapping versions (one in `CLAUDE.md`'s
Load-on-Demand preamble, one as `workflow.md`'s first bullet), is collapsed
into a single paragraph: act-then-show by default, with two named exceptions,
a new convention or design decision and anything outward-facing or
irreversible.

## Reason

[ADR 019](019-git-on-demand-via-skills.md) moved `git.md` to load-on-demand,
leaving `workflow.md` as the only file still `@`-imported into "Load Always."
Nothing consumes it as a standalone import - it's unconditionally inlined
every session either way - so the separate file bought organization, not
context savings or reuse.

[ADR 008](008-outward-irreversible.md) originally specified the principle be
"stated once in `CLAUDE.md` and applied in `conventions/workflow.md` and
`conventions/git.md`." That had drifted: `CLAUDE.md` stated one exception
(outward/irreversible actions), `workflow.md` stated a different exception
(new conventions/design decisions) under the same "act-then-show" name, in
two files. Folding workflow.md in and writing the statement once restores
008's original intent rather than changing its substance.

Alternatives rejected:

- **Keep workflow.md separate, just fix the duplication in place.** Leaves an
  always-`@`-imported single-purpose file with no on-demand consumer -
  organizational overhead with no longer any functional justification once
  git.md moved out.

## Consequences

- `CLAUDE.md`'s "Load Always" section now holds workflow content directly
  instead of importing it; the root `README.md` layout description is
  updated to match (no more `workflow.md` in `conventions/`).
- [ADR 002](002-always-on-vs-load-on-demand.md)'s tiering concept stands, but
  its always-on membership (`workflow`, `git`, `style`) is now entirely
  stale: `style` was removed per [ADR 013](013-style-rules-in-tooling-not-context.md),
  `git` moved on-demand per ADR 019, and `workflow` is folded in here. A
  pointer note is added there rather than marking it superseded, since the
  two-tier decision itself is unchanged.
- Future always-relevant rules get added directly to `CLAUDE.md`; there is no
  remaining precedent for a single-purpose always-on convention file.
