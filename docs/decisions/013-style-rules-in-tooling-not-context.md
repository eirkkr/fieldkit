# 013 - Style rules belong in deterministic tooling, not LLM context

## Decision

Prose style rules (spelling, punctuation, formatting) are not carried in agent
context as conventions. They are enforced by deterministic tools — linters,
scripts, CI checks — that run outside the LLM.

## Reason

An agent asked to follow a style convention is unreliable: it applies the rule
inconsistently, can't audit existing files exhaustively, and consumes tokens on
every session regardless of whether a violation is present. A deterministic tool
runs once, catches everything, costs nothing in LLM context, and produces the
same result every time.

Alternatives rejected:

- **Keep style rules in CLAUDE.md as always-on conventions.** Costs context on
  every session. Coverage is probabilistic — the agent may miss violations or
  flag false positives. Provides no safety net; a violation the agent misses
  reaches CI (or doesn't, with no enforcement at all).
- **Keep style rules as load-on-demand conventions.** Reduces the always-on
  cost, but the agent still has to be invoked to enforce them and coverage
  remains unreliable. Doesn't solve the fundamental problem.

## Consequences

- Each style rule needs a corresponding tool before it can be enforced. If no
  tool exists yet, enforcement is deferred until one is found or written —
  preferring a gap to an unreliable agent rule.
- Consumer repos inherit only the tooling that travels via the kit (scripts,
  config); per-repo rules are wired up per-repo.
- `conventions/style.md` has been removed. Any future style rules follow this
  decision: land the tooling first, then the rule is implicit in the check.
