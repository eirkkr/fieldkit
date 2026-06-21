# 004 - Lint with uvx rather than a uv project

## Decision

Markdown linting runs `pymarkdownlnt` through `uvx` at a pinned version
(`uvx pymarkdownlnt@0.9.38`) from the justfile, with rule config in
`.pymarkdown`. There is no `pyproject.toml`, lockfile, or virtual environment.

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
- `.pymarkdown` is the linter's default config name, so direct `pymarkdownlnt`
  invocations pick it up too.
