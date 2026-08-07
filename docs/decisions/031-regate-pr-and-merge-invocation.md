# 031 - Re-gate opening a PR and merging behind confirmation, unless directly invoked

## Decision

Opening a PR and merging go back to being approval-gated, but narrower than
the pre-028 gate: the gate is on *whether to invoke* `skills/pr/SKILL.md` or
`skills/merge/SKILL.md` at all, not on the draft each produces once running.
If the user types `/pr` or `/merge` directly, that invocation is itself the
approval - the skill runs straight through exactly as 028/029/030 left it,
with no draft shown for review first. If instead the caller (Claude) decides
mid-task, unprompted, that opening a PR or merging is the next step, it asks
first; only on a yes does it invoke the skill, which then runs the same
ungated draft-and-execute flow as the direct path.

`CLAUDE.md`'s Always-on section states this split. `skills/pr/SKILL.md` and
`skills/merge/SKILL.md` are reworded to say the invocation itself (direct or
approved) is what grants approval, rather than claiming to be unconditionally
act-then-show.

Push stays exactly as 027/029 left it: fully act-then-show in all cases,
including revising a stale PR description as part of a push. This decision
doesn't touch that.

This amends [028](028-ungate-pr-creation.md) and [030](030-ungate-merge.md).

## Reason

028/029/030 read "the human doesn't need to review the drafted title/body/
squash message before it runs" as license to drop the gate on the decision
to act at all. In practice the two collapsed into the same skill, so
ungating the review of the *draft* also ungated the *decision to open a PR
or merge*, and the caller started chaining straight from a push into
opening a PR or merging without being asked - not what was wanted. The two
are separable: the draft still doesn't need a pre-execution review (that
part of 028/029/030's trust holds and isn't revisited here), but the
decision to run `pr` or `merge` unprompted does need a yes first, same as it
did before 028.

Direct `/pr`/`/merge` invocation is unambiguous intent and needs no separate
gate - asking "should I open the PR?" right after the user typed `/pr` would
be asking about the thing they just asked for.

Alternatives rejected:

- **Fully revert 028/029/030**, restoring the pre-execution draft review too.
  Rejected - not what was asked; the draft-review step was never the
  complaint, only the unprompted invocation was.
- **Gate push as well**, treating the trio uniformly. Rejected - explicitly
  ruled out; push stays the one fully automatic action.

## Consequences

- `CLAUDE.md`'s Always-on section splits into a push bullet (ungated, as
  before) and a pr/merge bullet (gated unless directly slash-invoked).
- `skills/pr/SKILL.md` and `skills/merge/SKILL.md` no longer describe
  themselves as unconditionally act-then-show; they describe the invocation
  itself as the approval, then proceed exactly as before.
- The gate now lives one level up from where 028/030 removed it: in the
  decision to call the skill, not inside the skill. This relies on Claude
  correctly distinguishing "the user typed the slash command" from "I
  decided to invoke this" each time - there's no stored state backing it, so
  if that distinction proves unreliable in practice, it's worth revisiting.
