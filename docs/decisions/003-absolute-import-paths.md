# 003 - Use absolute paths in CLAUDE.md

## Decision

The imports and on-demand references in `CLAUDE.md` use absolute paths rooted at
the fixed clone location (`~/src/fieldkit/...`), not relative paths.

## Reason

The load-on-demand references (see
[ADR 002](002-always-on-vs-load-on-demand.md)) are read by the agent during a
consumer session, where the working directory is the consumer repo, not this
one. A relative path like `conventions/github.md` would resolve against the
consumer and miss. Relative paths were rejected for this reason; absolute paths
resolve correctly from anywhere. The same choice is applied to the `@`-imports
for consistency, even though those resolve relative to the containing file.

## Consequences

- The clone must live at `~/src/fieldkit`; the README documents this as a setup
  step and the path is hardcoded throughout `CLAUDE.md`.
- Relocating the kit means updating those paths (and any consumer import lines).
