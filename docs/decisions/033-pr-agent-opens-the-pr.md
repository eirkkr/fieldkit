# 033 - Let the pr agent open the PR itself

## Decision

`agents/pr` runs `gh pr create` itself, as the last step of the same
tool-call boundary in which it verifies the base branch, the absence of a
duplicate PR, and the branch's push state. `skills/pr/SKILL.md` no longer
runs the command after the report comes back; its job ends at deciding the
title and body, dispatching, and relaying what the agent did. The agent's
frontmatter description changes from "Prep a pull request" to "Open a pull
request" to match.

This makes the trio uniform: `push` commits and pushes, `pr` opens the PR,
`merge` merges - each skill decides, each agent acts. It amends
[028](028-ungate-pr-creation.md), whose consequences put `gh pr create` in
the skill, and settles the cross-reference [030](030-ungate-merge.md) made
to `pr`'s old shape when it chose the opposite split for `merge`.

The approval model is untouched. [031](031-regate-pr-and-merge-invocation.md)
still governs *whether* the skill is invoked - the user typing `/pr`, or the
caller asking and getting a yes. All this decision moves is which half of an
already-approved pair types the command.

## Reason

The split existed to protect an approval gate that no longer sits where it
did. [015](015-mechanical-subagent-boundary.md) warned that separating a
drafted, approved artifact from its execution "opens a seam where the
executing subagent could re-derive slightly different content than what was
approved". That risk needed a draft the agent could re-derive. Since
[027](027-push-decisions-move-to-caller.md) the caller hands the agent a
finished title and body and the agent is told to take them verbatim, so
moving `gh pr create` one hop inward re-derives nothing - it passes the same
strings to the same command. `merge` already demonstrates the shape:
[030](030-ungate-merge.md) put the squash message in the caller and the
`gh pr merge` call in the agent for exactly this reason, and noted the seam
concern doesn't apply once there's no approval step between draft and
execution.

The split also had a live failure mode, which is what prompted this. The
agent would report a compare link and the drafted title and body - an
artifact that reads as finished work - and the orchestrator would relay it
and stop, leaving no PR open. Nothing in the report said "now run
`gh pr create`", and the instruction to do so lived in the skill, which by
then was several hundred lines of transcript back. The instruction was
followed correctly by the agent and missed by the caller, which points at
the handoff rather than at either party.

What is left in the agent once creation is removed is also too thin to earn
a subagent hop under [015](015-mechanical-subagent-boundary.md)'s own test
("is it ungated, and is there enough real work to justify the isolation"):
three read-only `gh`/`git` checks and a string-built compare link. Folding
the creation back in restores the isolation's value rather than removing it.

Alternatives rejected:

- **Keep the split, but make the handoff unmissable** - end the agent's
  report with the literal `gh pr create` invocation for the caller to run.
  Fixes the observed miss, but by adding ceremony to preserve a seam whose
  original justification is gone, and it leaves the trio asymmetric for a
  reader to re-derive later.
- **Drop `agents/pr` and inline everything into the skill.** Consistent in
  its own way, but loses what [016](016-skill-agent-pair.md) pairs an agent
  for: a pinned cheap model and a narrow tool list, enforced structurally
  rather than by prose in the invocation.
- **Move `merge` the other way**, splitting its execution out to match `pr`'s
  old shape. Backwards - [030](030-ungate-merge.md) already argued the
  single-boundary version is the better one, and it has the stronger case,
  since its defensive CI re-check and the merge call want to be adjacent.

## Consequences

- `skills/pr/SKILL.md` shrinks back toward the thin dispatch-and-relay shape
  [016](016-skill-agent-pair.md) describes, and says explicitly not to run
  `gh pr create` - the miss this ADR fixes was a caller doing too much, so
  the correction has to be stated on the caller's side too.
- A duplicate-PR check now guards an action rather than a report, so step 2
  of the agent is load-bearing: if it is wrong, a second PR gets opened
  rather than a stale link getting relayed.
- `agents/pr` no longer builds a compare link, since the created PR's own
  URL supersedes it.
- The trio now reads uniformly - skill decides, agent acts - which is worth
  more than any one of the three splits individually, because it removes the
  question of which half acts each time one of them is invoked.
