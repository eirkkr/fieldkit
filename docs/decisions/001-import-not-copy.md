# 001 - Distribute conventions by @-import, not per-repo copies

## Decision

Consumer repos consume the shared conventions by `@`-importing them from a
single clone of this repo (e.g. `@~/src/fieldkit/CLAUDE.md`), rather than
copying or templating the convention text into each repo.

## Reason

The point of a shared kit is a single source of truth: a rule changed here
should take effect everywhere on the next session, with no per-repo sync step.
Copying the text into each consumer was rejected - copies drift, and keeping
them aligned by hand recreates the duplication the kit exists to remove.

## Consequences

- Editing a file here affects every consumer, so changes carry repo-wide weight.
- Consumers depend on the clone existing at a known path (see
  [ADR 003](003-absolute-import-paths.md)).
- The kit ships a thin `CLAUDE.md` entry point that imports the conventions, so
  a consumer adds one line rather than wiring each file.
