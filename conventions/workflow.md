# Working conventions

- When proposing new doc/convention text, show it and wait for approval before
  editing.
- Anything learned that's worth keeping goes in docs or CLAUDE.md, not
  machine-local memory (which isn't on other machines or available to other
  developers). Route by scope: generic, cross-repo lessons into the shared
  conventions kit; repo-specific ones into that repo's own docs.
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), check
  whether the underlying issue can be fixed instead. Suppress only when the tool
  is genuinely wrong about the file's context.

## Design decisions

- Record non-obvious design decisions - rationale plus alternatives rejected -
  as a numbered ADR in `docs/decisions/`, not in memory or a convention doc
  (those hold rules to follow, not the reasoning behind them). See
  `conventions/decisions.md` for the format and register.

## Reviewing and auditing

- A green CI / lint pass confirms only machine-enforced rules. Conventions
  enforced by review (ordering, spacing, doc accuracy, etc.) are invisible to it
  - audit them by hand against the diff; don't defer to CI.
- When a branch introduces or changes a convention, audit existing code for
  violations of it - the branch may not have corrected them - and bring any docs
  that still teach the old pattern into line.
- When editing a file, fix pre-existing violations of documented conventions in
  that file as part of the change; don't extend them. Stay within files you're
  already touching - if the fix would span modules, file an issue instead.
