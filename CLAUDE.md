# Claude Guidance (Generic)

Shared dev conventions for use across repos. A consumer repo pulls these in by
`@`-importing this file (or individual `conventions/*` files) from its own
CLAUDE.md via a `.fieldkit` symlink to this repo - e.g. `@.fieldkit/CLAUDE.md`.
See the README for the one-time symlink setup.

- If a request would produce output that conflicts with these conventions, flag
  it briefly before proceeding rather than silently complying.
- These are the generic, cross-repo rules. Repo-specific conventions, setup, and
  architecture live in the consumer repo's own docs.

## Always-on

- Act-then-show by default: make the change, surface it for review, correct
  after. Agree direction first, before acting, in two cases: a genuinely new
  convention or design decision (even when the action itself is local), and
  anything outward-facing or irreversible - creating or editing an issue or
  comment, opening a PR, or merging.
- Anything learned that's worth keeping goes in docs or CLAUDE.md. Route by
  scope: generic cross-repo lessons into the shared conventions kit;
  repo-specific ones into that repo's own docs.
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), check
  whether the underlying issue can be fixed instead. Suppress only when the
  tool is genuinely wrong about the file's context (e.g. a generated or
  vendored file).
- Delegate to a subagent for context isolation - keeping a large, throwaway
  exploration out of the main window - not to put a cheaper model on a small
  task. A fresh subagent re-pays context from scratch, which dominates a
  small task's cost.

### Linting and formatting

- Don't run formatters or linters unless asked - the human runs these and CI
  enforces them. Match the surrounding style; don't count line lengths or
  reflow prose to hit a column. Wrap by eye and leave any off-by-one to CI.
- This division is deliberate: a style slip reaching CI is a cost the human
  accepts in exchange for not burning tokens on lint/format churn.
- Tests are different: run them to verify code you wrote - correctness
  feedback, not churn. Use the repo's canonical command with quiet and
  short-traceback flags, failing fast while iterating.
- Run the narrowest relevant selection while iterating; widen to the full
  suite before declaring work done.

### Reviewing and auditing

- A green CI / lint pass confirms only machine-enforced rules. Audit
  conventions enforced by review (ordering, spacing, doc accuracy) by hand
  against the diff.
- When a branch introduces or changes a convention, audit existing code for
  violations and bring any docs that still teach the old pattern into line.
- When editing a file, fix pre-existing convention violations in that file as
  part of the change; don't extend them. If the fix would span modules, file
  an issue instead.

## Load on Demand

Situational conventions, not carried in context. Read the matching file before
the action; don't load it otherwise.

Branch, commit, PR, and merge actions normally go through the `push`, `pr`,
and `merge` skills - each reads `git.md`/`github.md` itself. Read those
directly only for a git or GitHub action the skills don't cover.

<!-- Read-tool targets (not @-imports). Paths are relative to the consumer
repo root - the directory the session is started from. Read
.fieldkit/conventions/<file> from there, via the .fieldkit symlink. -->

| Before...                                                                       | Read                               |
| ------------------------------------------------------------------------------- | ---------------------------------- |
| A git action `push`/`pr`/`merge` don't cover (rebase, tag, amend)               | .fieldkit/conventions/git.md       |
| A GitHub action `pr`/`merge` don't cover (issues, comments, PR edits)           | .fieldkit/conventions/github.md    |
| Recording a design decision (ADR)                                               | .fieldkit/conventions/decisions.md |
| Writing an implementation spec or plan                                          | .fieldkit/conventions/specs.md     |
| Building a feature that calls an LLM                                            | .fieldkit/conventions/ai.md        |
