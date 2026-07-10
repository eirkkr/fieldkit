# 015 - Delegate mechanical, ungated git steps only

## Decision

`agents/commit-push` delegates the commit-and-push step to a subagent (cheap
model, isolated context, reads `conventions/git.md` itself). PR creation and
merging stay in the main agent - they are not split into subagents of their
own, and the always-loaded convention docs (`workflow.md`, `git.md`) stay
loaded rather than being trimmed on the assumption subagents cover them.

## Reason

Commit/push fits delegation for two reasons: `workflow.md`'s act-then-show
rule means no approval gate blocks it, and there's real work to isolate
(reading the diff, deciding a branch name, drafting the message) that a
cheaper, throwaway context suits well.

PR creation and merge don't fit the same shape:

- Both require a draft (PR title/body, or the squash-merge message) shown to
  the user and approved *before* the action runs. By the time a subagent
  would be invoked, all the judgment is already spent - what's left is a
  single already-approved `gh pr create`/`gh pr merge` call. There's little
  to isolate, so a subagent hop mostly adds cold-start overhead.
- Splitting drafting (main agent, pre-approval) from execution (a second
  subagent) opens a seam where the executing subagent could re-derive
  slightly different content than what was approved - undermining the point
  of the approval gate.

Loading `git.md`/`workflow.md` always was also reconsidered, since the
subagent can read the doc itself when invoked. Rejected: those docs encode
policy the *orchestrator* has to hold regardless of any subagent - approval
gates on PR/merge, branch naming decided during planning before any commit
exists - and the doc is cheap to keep resident. Fragmenting further steps
into subagents to avoid loading a small file trades a negligible context
cost for repeated subagent overhead, the wrong trade.

## Consequences

- Only steps that are both ungated (act-then-show) and substantial enough to
  warrant an isolated, cheaper context get their own subagent. PR/merge
  mechanics stay inline in the main agent, executed in the same turn as the
  approval they follow.
- `conventions/workflow.md` and `conventions/git.md` stay in CLAUDE.md's
  "Load Always" tier; `agents/commit-push/AGENT.md` re-reads `git.md`
  independently since its context doesn't inherit the main agent's.
- Future mechanical steps should be judged against this same test before
  becoming a subagent: is it ungated, and is there enough real work to
  justify the isolation.

## Superseded

Superseded by [ADR 019](019-git-on-demand-via-skills.md): `pr-prep` and
`merge-prep` subagents now exist for PR/merge drafting, and branch creation
moved into `/push`'s worker agent - both premises this ADR argued from no
longer hold.
