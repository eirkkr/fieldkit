# Claude Guidance (Generic)

Shared dev conventions for use across repos. A consumer repo pulls these in by
`@`-importing this file (or individual `conventions/*` files) from its own
CLAUDE.md via a `.fieldkit` symlink to this repo - e.g. `@.fieldkit/KIT.md`.
See the README for the one-time symlink setup. The kit's own repo-specific
rules live in its root `CLAUDE.md`, which is not imported by consumers.

- These are the generic, cross-repo rules - repo-specific conventions, setup,
  and architecture live in the consumer repo's own docs. Flag conflicts with
  them briefly before proceeding, rather than silently complying.

## Always-on

- Act-then-show by default: make the change, surface it, correct after. Ask
  first for the actions the table marks that way, for anything else
  outward-facing or irreversible, and for a genuinely new convention or
  design decision - that last one is gated even when the change itself is
  local.
- Git and GitHub actions go through the `push`, `pr`, and `merge` skills -
  don't reach for `git commit`, `git push`, `gh pr create`, or `gh pr merge`
  directly, even mid-task and even when the step looks trivial. Read-only
  inspection (`git status`, `git diff`, `git log`) stays direct, as do
  actions no skill covers - read the matching doc below for those.

| Action                                     | Approval      | Notes                                                          |
| ------------------------------------------ | ------------- | -------------------------------------------------------------- |
| Committing and pushing                     | act-then-show | each coherent piece as it lands, not one batch per session     |
| Revising an open PR's title/body           | act-then-show | keep it true as the branch grows                               |
| Filing an issue                            | ask first     | unless the user asked for one                                  |
| Commenting on an issue, editing either     | act-then-show | surface what was filed so it can be corrected                  |
| Closing an issue                           | ask first     | except the automatic close of a `Closes #X` PR on merge        |
| Creating a branch off a non-default branch | ask first     | explain why first; off the default branch it needs no approval |
| Opening a PR                               | ask first     | unless the user typed `/pr`                                    |
| Merging                                    | ask first     | unless the user typed `/merge`; also conditioned on CI         |

- Typing `/pr` or `/merge` is itself the approval, and covers the push it may
  need first; asking for an issue is the same. Approval is for whether to
  act, not a preview of the draft: draft it and go straight to it.
- An issue settles that a finding is handled later and separately, which
  forecloses doing it now on the branch in hand. Say what the issue would
  say, and file it on a yes.
- Merging is conditioned on CI on top of approval - a failed check or a
  conflict stops it (report that, don't merge around it), a still-running
  check is waited out, a green one merges with no further sign-off.
- The PR a review-gated change opens at each stage's gate (see
  `conventions/specs.md`) needs no approval - one per stage, and opening it
  is part of reaching the gate. Each one's merge is gated like any other.
- Default to committing onto whatever branch you're already on, even if its
  existing work looks unrelated. New branches come off the default branch
  (see git.md); stacking one on another is an anti-pattern, and where that
  seems genuinely warranted it's the same gate.
- A gate on a *follow-up* never gates the action that precedes it - don't
  hold a push on an unrelated open question; land it, then ask.
- Route anything learned that's worth keeping by scope: generic cross-repo
  lessons into the shared conventions kit, repo-specific ones into that
  repo's own docs.
- `conventions/*.md` are read by humans and agents alike - state git/GitHub
  mechanics as plain facts, not instructions to an agent. This file's own
  process vocabulary (act-then-show, gate, dispatching a subagent) belongs
  here or in the skill/agent files that execute it, never in a `conventions`
  doc - a human reading one shouldn't need `KIT.md` open to parse a term
  in it.
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), try
  fixing the underlying issue first. Suppress only when the tool is
  genuinely wrong about the file's context (e.g. a generated or vendored
  file).
- An exemption list records why each entry is exempt, in terms of the rule
  it escapes. An entry describing what the code does instead ("uses the
  raw driver", "runs at startup") cannot be audited: nothing in it says
  whether a new case belongs, so the list grows by precedent. Write each
  reason so it could be used to refuse an entry.
- Known violations of a convention live in the issue tracker, not in the
  convention document - the document outlives them, and a stale list of
  files reads as permission.
- Delegate to a subagent for context isolation - keeping large, throwaway
  exploration out of the main window - not for a cheaper model on a small
  task. A fresh subagent re-pays context from scratch, which dominates a
  small task's cost.
- A count, or a claim about a file's contents, is re-derived from the
  tree as it is written into an ADR, spec, issue or commit message -
  never recalled, never carried over from an older document. Stale
  figures get repeated precisely because they are already written down.
- An issue, ADR or spec is read by someone who has none of the conversation
  that produced it. Everything needed to act on it belongs in the body: the
  decisions still open, the docs that must change alongside the code, the
  reasoning behind a choice that looks arbitrary without it. Catching
  yourself planning to brief the next session is the signal that something
  is missing from the artifact.
- A later finding that changes what the body says is edited into the body,
  not left in a comment beneath it. Someone acting on the body alone must
  not be acting on a version already known to be superseded.
- Reading part of a file is not reading it. "This document never
  addresses X", drawn from a head-and-tail skim, is a claim about the
  part that was not read.

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
- An artifact edited many times needs reading end to end, as a document,
  before it is called finished. Every edit can be correct while the whole
  stops describing itself - the usual symptom is a stated goal the body
  has outgrown. A separate pass from auditing the diff, and it comes
  last.
- Auditing prose for a phrase needs the text unwrapped first - hard-wrapped
  Markdown splits phrases across lines, where a line-based `grep` misses them
  and reports the file clean. Normalise whitespace before matching (e.g. read
  the file and `' '.join(text.split())`), and treat a no-hit result from a
  line-based search over wrapped prose as unproven, not as absence.

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
