# 004 - Lint with uvx rather than a uv project

## Decision

Markdown linting runs `rumdl` through `uvx` at a pinned version
(`uvx rumdl@0.2.26`) from the justfile. There is no `pyproject.toml`, lockfile,
or virtual environment.

## Reason

This repo has no application code or runtime dependencies - only a single
linter. A full uv project (the studynav approach: `pyproject.toml`, `uv.lock`,
`uv sync`) was rejected as overhead disproportionate to one tool: it would add
an install step and project scaffolding for no other benefit. `uvx` runs the
tool on demand with no install, and pinning the version in the recipe gives
reproducible results without a lockfile.

## Consequences

- `just check` / `just fix` work with no setup beyond `just` and `uv`.
- Upgrading the linter means editing the pinned version in the justfile rather
  than running a lock update.
- rumdl's built-in defaults (line-length=80, tables exempt) match the project
  requirements, so no config file is needed.
