# 027 - Move push's judgment calls to the caller; agent stays mechanical

## Decision

`skills/push/SKILL.md` (the orchestrator, i.e. whatever invoked `/push`) now
decides the branch name, the commit message, the exact file list, and -
when the target branch already has an open PR - whether its description has
gone stale and what the revision should be. `agents/push/AGENT.md` (renamed
from `commit-push`, so the agent name matches the skill) takes all of it as
given: it no longer runs `git diff` to draft a message, infers a branch name
or type, discovers which files changed, or reads a PR to judge staleness.
Its only PR-related step left is mechanical - run `gh pr edit` if handed
exact, already-approved title/body text; otherwise leave the PR alone and
just carry its link through the report. Its model drops from `sonnet` to
`haiku`, since no drafting or judgment happens in its context anymore.

The push itself stays unblocked by PR-approval, unchanged from ADR 026: the
skill dispatches the push right away, and only waits on a still-pending PR
draft's approval, which gates the `gh pr edit`, never the push.

This amends [016](016-skill-agent-pair.md), [019](019-git-on-demand-via-skills.md),
and [026](026-pr-description-sync-on-push.md); none is superseded outright.

## Reason

The agent runs in an isolated context that inherits nothing from the
conversation that triggered `/push` - by ADR 015's original design, so it
re-reads `conventions/git.md` and reconstructs intent from the diff itself.
That isolation was worth paying for when the agent had real drafting work to
do. It stopped being worth it once the orchestrator was asked to do the same
work: the orchestrator already knows what changed and why - it made the
change - so having the agent re-derive a branch name, a commit message, or a
staleness verdict from `git diff` in a fresh context duplicates judgment the
caller already holds, at the cost of a colder, less-informed pass. Passing
the decision through explicitly is strictly cheaper and no less accurate.

What's left in the agent - branching off default, staging named files,
committing, pushing, optionally applying an approved `gh pr edit` - is
execution with no open judgment calls, which is what ADR 015 called the
correct shape for a delegated subagent in the first place. A cheaper model
is a direct consequence, not a separate decision: nothing left in the
agent's job benefits from `sonnet` over `haiku`.

Alternatives rejected:

- **Leave staleness-checking in the agent, only move branch/message/files.**
  Inconsistent split - the same "caller already has the diff" argument that
  moves commit-message drafting out applies just as much to the PR-body
  comparison ADR 026 gave the agent. Splitting judgment across two contexts
  (agent judges staleness, caller judges everything else) is harder to
  reason about than either agent deciding nothing or everything.
- **Keep the agent deciding everything, just document it better.** Doesn't
  address the actual cost: a fresh, isolated context re-deriving what the
  orchestrator already knows.
- **Always require pre-approved PR content before dispatching the push, so
  the agent never needs a bare "PR is open" fallback.** Rejected because it
  would gate the push on the same approval ADR 026 explicitly carved the
  push out of - a regression, not a simplification.

## Consequences

- `agents/push/` replaces `agents/commit-push/`; `subagent_type: push`.
  [016](016-skill-agent-pair.md)'s "nothing requires the skill and agent
  names to match" still holds generally (`pr-prep`, `merge-prep` don't
  match) - `push` simply chose to.
- [016](016-skill-agent-pair.md)'s "the skill must stay thin ... task logic
  accumulating in `SKILL.md` is a sign the split has eroded" no longer
  describes `push`: `SKILL.md` now holds real decision logic (branch,
  message, files, staleness). That's not the erosion 016 warned against -
  the logic isn't reimplementing the agent's mechanical work, it's the
  orchestrator using context the agent structurally can't have. Future
  skill/agent pairs should judge "thin" by that distinction, not by line
  count in `SKILL.md`.
- [019](019-git-on-demand-via-skills.md)'s branch-naming-in-the-agent
  behavior reverts to the caller; the ADR's actual tiering decision
  (`git.md` on the Load-on-Demand table) is untouched - `skills/push`
  reads it directly instead of `agents/push`.
- [026](026-pr-description-sync-on-push.md)'s gate (approval before
  `gh pr edit`, push itself never gated) is untouched; only who performs the
  comparison and drafts the revision moves, from the agent to the caller.
- The agent's report can no longer double as the human-facing staleness
  detector - the caller has to remember to run the check itself. Nothing
  structural catches a caller that skips it, the same trust `git.md` and
  `github.md` already place in the orchestrator elsewhere.
