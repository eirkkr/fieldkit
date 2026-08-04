# 019 - Route git actions through skills; git.md on demand

## Decision

`conventions/git.md` moves from `CLAUDE.md`'s "Load Always" tier to the
"Load on Demand" table, alongside `github.md`, with a row directing to it for
any git action the `push`, `pr`, or `merge` skills don't cover.
`agents/commit-push/AGENT.md` (behind `/push`) now creates the branch itself
when the current branch is the repo's default branch, choosing a
`type/short-description` name per `git.md`, instead of assuming the
orchestrator already branched.

This supersedes [ADR 015](015-mechanical-subagent-boundary.md): both reasons
it gave for keeping `git.md` resident no longer hold.

## Reason

ADR 015 kept `git.md` always-loaded for two reasons: branch naming was an
orchestrator-level judgment made "during planning, before any commit exists,"
and PR/merge mechanics stayed in the main agent rather than subagents, so the
approval-gate policy had to live in main context. Both premises are gone now:
branch creation happens inside `/push`'s worker agent, which already re-reads
`git.md` itself (the ADR 016 isolation pattern), so the orchestrator no
longer needs the naming rules resident to make that call. And `pr-prep` /
`merge-prep` subagents now exist for PR and merge drafting - `skills/pr` and
`skills/merge` each restate the approval gate inline ("wait for approval
before...") rather than depending solely on `git.md` being loaded.

The one rule ADR 002 chose to hedge inline - approval before outward-facing
or irreversible actions - already lives in `CLAUDE.md`'s Load-on-Demand
preamble, independent of `git.md`'s tier. The remaining content ("never
commit to main," branch/commit format) is now partly enforced structurally
too: `/push` always branches off the default branch before committing rather
than only being told not to commit to main. This follows the tiering ADR 002
already set up - `github.md` has lived on demand since then for the same
reason.

Alternatives rejected:

- **Keep `git.md` always-loaded and just add branch creation to `/push`.**
  Once every git action funnels through `push`/`pr`/`merge` and those skills
  self-read the doc, keeping it resident duplicates cost for no remaining
  benefit - the trade ADR 015 warned against, inverted now that the isolation
  exists.
- **Inline the full `git.md` ruleset into `CLAUDE.md`'s hedge paragraph**
  instead of demoting the file. Rejected: recreates the content twice and
  invites drift; the skills already read the source of truth themselves.

## Consequences

- `conventions/git.md` no longer costs context in every session; only
  sessions doing a git action outside `push`/`pr`/`merge` (rebase, amend,
  tag, a manual commit) pay to read it, the same trade `github.md` already
  makes.
- ADR 015 is superseded; its status is updated with a pointer to this ADR.
- `agents/commit-push/AGENT.md` can now create branches as well as
  commit/push, widening its blast radius slightly - but branch creation is
  reversible and stays within ADR 015's ungated, act-then-show test.
- Direct git or GitHub work outside the three skills must still read the
  matching convention doc first per the Load-on-Demand table; nothing is
  removed, only demoted.

> Amended by [025](025-skill-routing-stated-always-on.md): the routing rule
> itself moves from the Load-on-Demand preamble to an Always-on bullet, since
> the preamble is only read once the agent already suspects it needs a lookup.
> `git.md`'s on-demand tier, decided here, stands.
