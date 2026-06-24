# Working conventions

- When proposing new doc/convention text, show it and wait for approval before
  editing.
- Anything learned that's worth keeping goes in docs or CLAUDE.md, not
  machine-local memory (which isn't on other machines or available to other
  developers). Route by scope: generic, cross-repo lessons into the shared
  conventions kit; repo-specific ones into that repo's own docs.
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), check
  whether the underlying issue can be fixed instead. Suppress only when the tool
  is genuinely wrong about the file's context (e.g. a generated or vendored
  file). A `type: ignore[unreachable]` on a branch condition almost always means
  the condition itself is wrong, not the type checker.

## Linting and formatting

- Don't run formatters or linters, and don't gate your work on them, unless
  asked - the human runs these and CI enforces them. Match the surrounding
  style and rely on normal care while writing; don't run a linter to discover
  problems.
- This division is deliberate: a style slip or a stray defect reaching CI is a
  cost the human accepts in exchange for not burning tokens on lint/format
  churn. "Lint must pass before push/merge" (if a consumer repo states it) is
  CI's job and the human's, not a gate the agent drives.

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
