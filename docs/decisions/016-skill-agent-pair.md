# 016 - Pair a thin skill with a worker agent for delegated tasks

## Decision

When a task is delegated per ADR 015's test, structure it as two files, not
one: a thin `skills/<name>/SKILL.md` that the main agent invokes as the entry
point, and a `agents/<name>/AGENT.md` that is the actual isolated worker
(pinned model, its own tool list, its own read of the relevant convention
docs). The skill's whole job is to dispatch to the agent with a short brief
and relay its report; it holds no task logic itself. Both halves are
distributed the same way - symlinked out to consumers by `just install`
(`skills/` into `~/.claude/skills`, `agents/` into `~/.claude/agents`), per
ADR 014's pull-style mechanism, now extended to agents.

`commit-push` is the first instance: `skills/push/SKILL.md` dispatches to
`subagent_type: commit-push`, defined in `agents/commit-push/AGENT.md`. The
skill name is shortened for typing frequency; nothing requires the skill and
agent directory names to match, as `pr`/`pr-prep` and `merge`/`merge-prep`
also show.

## Reason

A single combined file (a skill that inlines a large prompt and just tells
the model to "act cheaply") can't pin a model or a tool list - those are
properties of an agent definition, not skill frontmatter. Splitting the two
means the constraint (cheap model, narrow tools) lives where the platform can
actually enforce it, while the skill stays a stable, tiny entry point that's
easy to invoke by name or description-match.

The pairing also keeps the isolation ADR 015 argued for: the agent's context
doesn't inherit the main conversation, so it re-reads whatever convention
docs it needs itself rather than trusting a stale summary passed down. The
skill's only added value is the dispatch brief (see the `git diff --stat`
follow-up: the main agent already knows what changed and why, so it passes a
short summary instead of making the agent reconstruct that from a full diff).

Alternatives rejected:

- **One file, a skill only, describing the delegation in prose** (the
  original `commit-push` draft). Works, but the model pin lives in the
  invocation instructions rather than being a structural property of what
  gets invoked - easy to drift or skip.
- **One file, an agent only, invoked directly by name.** Loses the stable,
  discoverable entry point a skill gives; description-matching and
  `argument-hint` are skill-frontmatter features an agent doesn't have.

## Consequences

- Future delegated tasks that pass ADR 015's test get this same two-file
  shape: skill for entry/dispatch, agent for the pinned-model isolated work.
- `scripts/link-skills.sh` and `scripts/link-agents.sh` both need updating
  (or a consumer needs to re-run `just install`) whenever a new pair is
  added; there is no single combined linker.
- The skill must stay thin - if task logic starts accumulating in the
  `SKILL.md` body instead of the `AGENT.md`, that's a sign the split has
  eroded.
