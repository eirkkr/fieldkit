# 039 - Compact the Always-on gate rules into a table

## Decision

`KIT.md`'s Always-on section states which actions are gated as a three-column
table - action, approval, note - preceded by the act-then-show default and the
skill-routing rule, and followed by the exceptions that don't fit a cell (the
`/pr` and `/merge` invocation carve-out, merging's CI condition, the
review-gated draft PR, the branch default, and the follow-up rule). The five
prose bullets that carried all of this are gone.

The reasoning behind each call goes with them. Why filing an issue is
act-then-show, why a branch is cheap enough to amend, why a `/pr` invocation
counts as approval - each already lives in the ADR that made the call, which
is where `conventions/decisions.md` says a reader asking "why this way?"
should land.

The tiering itself is unchanged: the gate rules stay always-on.

## Reason

`KIT.md` is resident in every session of every consumer repo, so its prose is
the most expensive in the kit. The Always-on section had reached 724 words -
more than `conventions/github.md` (321) and `conventions/git.md` (531)
combined, both of which are on-demand. The gate portion alone was 559.

That length was accretion, not content. Each ungating decision appended a
clause to an existing bullet rather than restating the rule:
[029](029-ungate-pr-body-edits.md) for PR description sync,
[031](031-regate-pr-and-merge-invocation.md) for the invocation carve-out,
[034](034-review-gated-openspec-schema.md) for the draft PR at a review gate,
and [038](038-ungate-issue-filing.md) for issues and the close exemption. The
result was that the current policy on any one action had to be reconstructed
from clauses layered across several sentences. A table holds one row per
action, and the next such decision edits a cell instead of appending to a
paragraph.

Alternatives rejected:

- **Demote the gate rules to a load-on-demand doc.** This is the obvious way
  to cut resident words, and it fails for the reason
  [025](025-skill-routing-stated-always-on.md) already gave: a pointer is
  only consulted once the agent suspects it needs a lookup, which is too late
  for "you may do this without asking" - by then it has already asked.
- **Split `github.md` and `git.md` into finer on-demand files** so issue work
  loads only issue rules. `github.md` is already mostly an issues file (only
  ~55 of its words are PR-only), each split adds a resident row to the
  Load-on-Demand table to save on-demand words in a subset of sessions, and
  cross-cutting rules - the public-repo naming rule spans issue text, PR
  descriptions, comments and commit messages - would have to be duplicated
  (the drift [019](019-git-on-demand-via-skills.md) rejected) or be missed
  for the artifacts they didn't get filed under.
- **Keep the prose and trim it.** Doesn't stop the accretion, which is the
  actual mechanism behind the growth.

## Consequences

- The Always-on section drops from 724 words to 606; the gate rules within it
  from 559 to 441, including the table. The saving is modest in words - the
  structural change is what stops the next decision adding to it.
- The "why" behind a gate is now only in the ADRs. A reader who wants it
  follows `docs/decisions/README.md`, and the rule they must follow is the
  cell.
- `KIT.md`'s CI line is corrected in passing: it still said a still-running
  check blocks merging outright, which [032](032-merge-waits-out-pending-ci.md)
  amended to "waited out". `conventions/git.md` and `skills/merge` were
  updated then; `KIT.md` was missed, and the compaction surfaced it.
- The merge-close exemption from [038](038-ungate-issue-filing.md) becomes
  visible always-on as a note on the "closing an issue" row, rather than
  living only in `conventions/github.md` where it depended on the merge path
  reading that file.
- A table row is a worse home for a rule with real nuance than a sentence is.
  Anything that outgrows its cell belongs in the footnotes under the table,
  not squeezed into the Notes column.
