# Decisions

Lightweight architecture decision records (ADRs) for non-obvious design choices.
See [conventions/decisions.md](../../conventions/decisions.md) for the format.

| #   | Decision                                                               | Status     |
| --- | ---------------------------------------------------------------------- | ---------- |
| 001 | [Distribute conventions by @-import](001-import-not-copy.md)           | Accepted   |
| 002 | [Tier always-on vs load-on-demand](002-always-on-vs-load-on-demand.md) | Accepted   |
| 003 | [Absolute paths in CLAUDE.md](003-absolute-import-paths.md)            | Superseded |
| 004 | [Lint with uvx, not a uv project](004-lint-via-uvx.md)                 | Accepted   |
| 005 | [Flat, content-shaped structure](005-flat-repo-structure.md)           | Accepted   |
| 006 | [Symlink kit reference](006-symlink-kit-reference.md)                  | Accepted   |
| 007 | [Agents don't run linters](007-agents-dont-run-linters.md)             | Accepted   |
| 008 | [Gate on outward or irreversible actions](008-outward-irreversible.md) | Accepted   |
| 009 | [User-level commands, per-repo conventions](009-user-level-commands-not-conventions.md) | Accepted   |
| 010 | [Python hub and on-demand spokes](010-python-hub-and-spokes.md)        | Accepted   |
| 011 | [WIP on branches; gate PR creation](011-wip-on-branches.md)            | Accepted   |
| 012 | [Per-consumer reconcile marker](012-reconcile-marker.md)                | Accepted   |
| 013 | [Style rules in tooling, not LLM context](013-style-rules-in-tooling-not-context.md) | Accepted   |
