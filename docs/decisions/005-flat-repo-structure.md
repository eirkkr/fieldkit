# 005 - Flat, content-shaped repo structure

## Decision

Conventions live at the top level in `conventions/`. The repo has no generic
`docs/` directory and no `DEVELOPMENT.md`; `docs/` exists only to hold
`decisions/` (these ADRs).

## Reason

In an application repo, `docs/` holds reference material beside the code and
`DEVELOPMENT.md` documents standing up an environment. Here the conventions are
the product, not a footnote to code, so they belong at the top level; and the
only "development" task is two lint commands, which fit a README section. An
app-shaped layout (a `docs/` reference tree, a `DEVELOPMENT.md`) was rejected as
empty ceremony - there is no secondary material to fill it.

## Consequences

- The repo surface stays small: `README.md`, `CLAUDE.md`, `conventions/`, and
  tooling config.
- `docs/decisions/` is the one justified `docs/` subtree, following this repo's
  own ADR convention rather than contradicting the structure.
