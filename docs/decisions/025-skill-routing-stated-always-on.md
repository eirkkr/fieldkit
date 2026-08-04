# 025 - State skill routing and push cadence always-on

## Decision

Two git rules move into `CLAUDE.md`'s Always-on tier as standalone bullets:

- Git and GitHub actions route through the `push`, `pr`, and `merge` skills;
  raw `git commit`/`git push`/`gh pr create`/`gh pr merge` are out, with
  read-only inspection and skill-uncovered actions (rebase, amend, tag)
  carved out.
- Committing and pushing a branch are ungated act-then-show, and commits
  should land per coherent piece of work rather than batched at session end.

`conventions/git.md` stays in the Load-on-Demand table; its preamble drops the
routing sentence, which the Always-on bullet now carries.

This amends [019](019-git-on-demand-via-skills.md), which established the
routing rule but sited it in the Load-on-Demand preamble. The tiering that ADR
set up is unchanged - `git.md` itself stays on demand.

## Reason

Resolves [issue #41](https://github.com/eirkkr/fieldkit/issues/41). ADR 019
already decided every git action funnels through the skills, but stated it in
a preamble under the "Load on Demand" heading. An agent only reads that
preamble once it already suspects a situational lookup is needed - and the
failure mode is precisely the agent *not* suspecting: it reaches for its own
built-in git playbook mid-task, commits directly, and never consults the
table. Two recorded occurrences (the session behind #41, and three commits
onto `main` in a consumer repo) share that shape. Always-on bullets are
weighed every turn, so the rule reaches the agent before it acts rather than
after it decides to look something up.

The push-cadence bullet rides along for the same structural reason. ADRs
[008](008-outward-irreversible.md) and [011](011-wip-on-branches.md) made
commits and branch pushes ungated, and `git.md` said "push freely" - but only
on demand, so an agent that never opened the file defaulted to its built-in
instinct to ask before pushing. Stating the permission positively, in the tier
that's always resident, is what makes it take effect.

Alternatives rejected:

- **`conventions/git.md` only** (issue #41's first option). It's the natural
  topical home, but it hasn't been always-loaded since ADR 019 - the same tier
  problem, one level down.
- **The skill's own description, relying on description-matching.** Simplest,
  and already in place; the sessions above show it doesn't fire when the agent
  never frames the step as needing a skill.
- **`conventions/workflow.md`** (issue #41's second option). That file no
  longer exists - [020](020-fold-workflow-into-claude-md.md) folded it into
  `CLAUDE.md`, which is where these bullets land anyway.
- **A `PreToolUse` hook blocking raw `git commit`.** Stronger enforcement, but
  Claude Code settings hooks don't travel through the `@.fieldkit` import (the
  constraint [023](023-block-default-branch-commits-via-hook.md) worked
  around), and the shipped `pre-commit` hook already backstops the worst
  outcome structurally.

## Consequences

- The Always-on tier grows by two bullets. Accepted: ADR 002's tiering trades
  context cost for reliability, and these are the rules whose whole value is
  being weighed before the agent acts.
- Routing is now stated in two places at different altitudes - the Always-on
  bullet (the rule) and the Load-on-Demand preamble (which rows to read when
  no skill covers the action). The preamble was rewritten to point at the
  bullet rather than restate it, avoiding the drift
  [020](020-fold-workflow-into-claude-md.md) had to clean up.
- Enforcement is still instruction-only for the routing rule; only
  default-branch commits are blocked structurally. A repeat occurrence would
  argue for the hook alternative above.
