# Working conventions

- Act-then-show: make the change, then surface it for review and correct after.
  Agree direction first only for genuinely new conventions or design decisions -
  refinements and routine edits need none.
- Anything learned that's worth keeping goes in docs or CLAUDE.md, not
  machine-local memory. Route by scope: generic cross-repo lessons into the
  shared conventions kit; repo-specific ones into that repo's own docs.
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), check
  whether the underlying issue can be fixed instead. Suppress only when the tool
  is genuinely wrong about the file's context (e.g. a generated or vendored
  file).
- Delegate to a subagent for context isolation - keeping a large, throwaway
  exploration out of the main window - not to put a cheaper model on a small
  task. A fresh subagent re-pays context from scratch, which dominates a small
  task's cost.

## Linting and formatting

- Don't run formatters or linters unless asked - the human runs these and CI
  enforces them. Match the surrounding style; don't count line lengths or reflow
  prose to hit a column. Wrap by eye and leave any off-by-one to CI.
- This division is deliberate: a style slip reaching CI is a cost the human
  accepts in exchange for not burning tokens on lint/format churn.
- Tests are different: run them to verify code you wrote - correctness feedback,
  not churn. Use the repo's canonical command with quiet and short-traceback
  flags, failing fast while iterating.
- Run the narrowest relevant selection while iterating; widen to the full suite
  before declaring work done.

## Design decisions

- Record non-obvious design decisions - rationale plus alternatives rejected - as
  a numbered ADR in `docs/decisions/`, not in memory or a convention doc. See
  `conventions/decisions.md` for the format and register.

## Reviewing and auditing

- A green CI / lint pass confirms only machine-enforced rules. Audit conventions
  enforced by review (ordering, spacing, doc accuracy) by hand against the diff.
- When a branch introduces or changes a convention, audit existing code for
  violations and bring any docs that still teach the old pattern into line.
- When editing a file, fix pre-existing convention violations in that file as
  part of the change; don't extend them. If the fix would span modules, file an
  issue instead.
