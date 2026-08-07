# Claude Guidance (Generic)

Shared dev conventions for use across repos. A consumer repo pulls these in by
`@`-importing this file (or individual `conventions/*` files) from its own
CLAUDE.md via a `.fieldkit` symlink to this repo - e.g. `@.fieldkit/CLAUDE.md`.
See the README for the one-time symlink setup.

- These are the generic, cross-repo rules - repo-specific conventions, setup,
  and architecture live in the consumer repo's own docs. Flag conflicts with
  them briefly before proceeding, rather than silently complying.

## Always-on

- Act-then-show by default: make the change, surface it, correct after.
  Agree direction first instead for two cases: a genuinely new convention or
  design decision, even if the action itself is local; and anything
  outward-facing or irreversible - creating or editing an issue or comment,
  opening a PR, or merging.
- Git and GitHub actions go through the `push`, `pr`, and `merge` skills -
  don't reach for `git commit`, `git push`, `gh pr create`, or `gh pr merge`
  directly, even mid-task and even when the step looks trivial. Read-only
  inspection (`git status`, `git diff`, `git log`) stays direct, as do
  actions no skill covers - read the matching doc below for those.
- Committing and pushing a branch are act-then-show - don't ask first. Commit
  each coherent piece of work as it lands and push it, rather than batching a
  session into one commit at the end. A branch is cheap to amend or discard,
  and the `pre-commit` hook keeps the default branch out of reach. The gates
  are opening a PR, merging, and editing an open PR's title or body - nothing
  else waits for approval. A gate on a *follow-up* never gates the push
  itself: push first, then raise whatever the push turned up. Flagging a
  conflict or an open question is likewise not a reason to hold the commit -
  land the work, then ask.
- Default to committing onto whatever branch you're already on, even if its
  existing work looks unrelated to what you're about to add. Reach for a new
  branch only when starting from the default branch, or when you're
  convinced the current branch's work is genuinely unrelated - and that
  conviction is a gate, unlike the commit it would precede: explain why and
  get confirmation *before* creating the branch, not after. New branches
  come off the default branch (see git.md); stacking one on another is an
  anti-pattern, and on the rare occasion that seems genuinely warranted
  instead, it's the same gate - explain why and confirm first.
- Route anything learned that's worth keeping by scope: generic cross-repo
  lessons into the shared conventions kit, repo-specific ones into that
  repo's own docs.
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), try
  fixing the underlying issue first. Suppress only when the tool is
  genuinely wrong about the file's context (e.g. a generated or vendored
  file).
- Delegate to a subagent for context isolation - keeping large, throwaway
  exploration out of the main window - not for a cheaper model on a small
  task. A fresh subagent re-pays context from scratch, which dominates a
  small task's cost.

### Linting and formatting

- Don't run formatters or linters unless asked, for code or docs alike - the
  human runs these and CI enforces them. Match the surrounding style: don't
  count line lengths or reflow prose to hit a column, and leave any
  off-by-one wrapping to CI.
- This division is deliberate: a style slip reaching CI is the accepted cost
  of not burning tokens on lint/format churn.
- Tests are different: run them for correctness feedback, not churn. Use the
  repo's canonical command with quiet, short-traceback flags, and fail fast
  while iterating.
- Run the narrowest relevant selection while iterating; widen to the full
  suite before declaring work done.

### Reviewing and auditing

- A green CI/lint pass confirms only machine-enforced rules; audit
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

The `push`, `pr`, and `merge` skills each read `git.md`/`github.md`
themselves, so routing through them (see Always-on) needs no lookup here. The
rows below are for the actions those skills don't cover.

<!-- Read-tool targets (not @-imports). Paths are relative to the consumer
repo root - the directory the session is started from. Read
.fieldkit/conventions/<file> from there, via the .fieldkit symlink. -->

| Before...                                                                       | Read                               |
| ------------------------------------------------------------------------------- | ---------------------------------- |
| A git action `push`/`pr`/`merge` don't cover (rebase, tag, amend)               | .fieldkit/conventions/git.md       |
| A GitHub action `pr`/`merge` don't cover (issues, comments, PR edits)           | .fieldkit/conventions/github.md    |
| Recording a design decision (ADR)                                               | .fieldkit/conventions/decisions.md |
| Working an OpenSpec change (repo has `openspec/`) or writing a spec by hand     | .fieldkit/conventions/specs.md     |
| Building a feature that calls an LLM                                            | .fieldkit/conventions/ai.md        |
