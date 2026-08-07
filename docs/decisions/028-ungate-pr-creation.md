# 028 - Make opening a PR act-then-show, not approval-gated

## Decision

Opening a PR drops out of the approval-gated list. `skills/pr/SKILL.md`
drafts the title and body itself (per the caller-decides redesign already in
place), runs `gh pr create` immediately, and surfaces the link, title, and
body afterward instead of waiting on approval first. `CLAUDE.md`'s
outward/irreversible gate list and `conventions/git.md`'s PR section are
updated to match: the gates still in force are merging, creating or editing
an issue or comment, and editing an *already-open* PR's title or body -
opening the PR itself is no longer one of them.

This amends [008](008-outward-irreversible.md) and
[011](011-wip-on-branches.md), both of which established or relocated the
PR-creation gate.

## Reason

The gate existed to stop the agent from unilaterally asserting a branch was
ready for review. That risk shrinks once the PR's content is trustworthy
without a human reading it first - and `/pr` now drafts from the same
full-context, convention-checked process the caller uses for everything
else it decides unattended (branch name, commit message, `Closes #X`
verification). The human has already decided they trust that output enough
to skip reviewing it pre-creation.

The same reasoning 008/011 used to leave branch pushes ungated applies here:
a PR is not the irreversible step, it is cheap to correct after the fact
(`gh pr edit`, or close and reopen) the same way a branch is cheap to amend.
What's genuinely irreversible - merging into `main`, seen by every
consumer - stays gated, along with editing an *open* PR's description,
which [026](026-pr-description-sync-on-push.md) already argued is a
different risk (clobbering human-written text a reviewer is relying on).

Alternatives rejected:

- **Keep the gate for content, drop it only for timing** (i.e. create
  immediately but still require approval before the title/body can be
  considered final). Doesn't remove the wait the human asked to drop; also
  redundant with the existing post-open edit gate, which already covers
  fixing a PR's description after creation.
- **Drop every PR-related gate, including merge.** Not what was asked, and
  merge remains the one step that's both irreversible and reaches every
  consumer - the risk 008 originally gated on is still live there.

## Consequences

- `CLAUDE.md`'s Always-on gate list no longer names "opening a PR"; only
  "creating or editing an issue or comment" and "merging" remain there, plus
  the separate, narrower gate on editing an *open* PR's title or body.
- `skills/pr/SKILL.md` no longer has a "wait for approval" step before
  `gh pr create` - it runs right after the subagent's report comes back.
- `conventions/git.md`'s "get approval before opening the PR" line is
  replaced with a description of the same act-then-show model already
  applied to branch pushes.
- A wrong PR is now corrected after the fact - same recourse the
  branch/commit act-then-show model already relies on, extended one step
  further down the workflow.

> Amended by [029](029-ungate-pr-body-edits.md): the "editing an *open*
> PR's title or body" gate this ADR left standing is dropped too, on the
> same reasoning extended one step further. Merging is now the only gate
> left in the `push`/`pr`/`merge` trio.
>
> Amended by [031](031-regate-pr-and-merge-invocation.md): the decision to
> invoke `/pr` at all is gated again when it isn't the user directly typing
> `/pr` - only the draft this ADR ungated stays ungated once the skill is
> running.
