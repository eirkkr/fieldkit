# 018 - Rely on human-activated venv instead of an inline `uv run` rule

## Decision

Drop the "prefix every Python invocation with `uv run`" rule. Instead, the
human activates the project venv (`source .venv/bin/activate`) before
launching Claude, so plain `python`, `pytest`, `ruff`, etc. already resolve to
the venv's binaries. `conventions/python/run.md` and its load-on-demand
entries are removed; there's no longer a rule for the agent to carry.

## Reason

The `uv run` prefix was a workaround for the agent's shell not having the
venv on `PATH`. That's better fixed upstream: once the human activates the
venv in the shell Claude inherits, every subprocess call already gets the
right Python with no per-command prefix and no instruction to remember or
apply. This removes a rule that applied to "nearly every command in a Python
repo" (per [ADR 010](010-python-hub-and-spokes.md)) at zero cost, rather than
keeping it inline to avoid a load-on-demand hop.

## Consequences

- `conventions/python/run.md` is deleted; the "Invoking Python" row in
  `CLAUDE.md` and the "Running any Python command" row in
  `conventions/python/README.md` are removed with it.
- If a session's shell doesn't have the venv active (human forgot, or a
  non-interactive environment), plain commands will silently hit the system
  Python. There's no agent-side check for this - the fix is to activate the
  venv, not to reintroduce a prefix workaround.
- Narrows [ADR 010](010-python-hub-and-spokes.md): drops the "`uv run` rule
  stays inline" clause, but the hub-and-spokes split it established is
  unchanged and this ADR doesn't supersede it.
