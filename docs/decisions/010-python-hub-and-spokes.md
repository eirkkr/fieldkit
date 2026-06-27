# 010 - Split the Python conventions into a hub and on-demand spokes

## Decision

`conventions/python.md` is a slim hub rather than the full body of Python
rules. It carries only the one universally-needed rule (prefix tool invocations
with `uv run`) plus a load-on-demand table indexing the detail, which now lives
in sibling files:

- `python-code.md` - docstrings, imports, member ordering, exception handling.
- `python-setup.md` - project scaffolding and dependency version pinning.
- `testing.md` - pytest conventions (pre-existing; now indexed by the hub).

A Python repo `@`-imports `python.md` as before; the spokes are read on demand
when the task calls for them. The Python-specific `testing.md` trigger moves out
of the top-level `CLAUDE.md` table (which loads for every repo) into the hub.

## Reason

`python.md` had grown to ~5.6K and was inlined into every Python session in
full, carrying rarely-needed material - project scaffolding, dependency pinning
tables - on every turn regardless of task. This is the same context-cost problem
[ADR 002](002-always-on-vs-load-on-demand.md) solved across the language-agnostic
conventions, so the fix is the same tiering applied one level down: keep the
baseline small, pull the rest in when relevant.

Routing through a per-language hub (rather than adding Python rows to the
top-level `CLAUDE.md` table) keeps Python triggers out of non-Python repos'
context and makes the Python set self-contained behind its single opt-in import.

The `uv run` rule stays inline because it applies to nearly every command in a
Python repo; deferring it behind a read would defeat the purpose, the same hedge
ADR 002 makes for the safety-critical GitHub rule.

## Consequences

- The split deepens the load-on-demand dependence on the agent reading a file
  when triggered - now two hops (hub, then spoke) for Python detail. The hub's
  table is the routing surface, so its triggers must stay legible.
- `python-code.md` is loaded for most edit-heavy sessions anyway; the clear win
  is keeping `python-setup.md` out of context except at init or dependency
  changes. Splitting at task boundaries, not per-rule, keeps the grain coarse
  enough to be worth it.
- Spokes are siblings under `conventions/`, consistent with the flat structure
  ([ADR 005](005-flat-repo-structure.md)); they link back to the hub for the
  index and the always-on rule.
