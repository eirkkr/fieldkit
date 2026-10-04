# Claude Guidance (Generic)

Generic rules shared across repos, imported from a consumer's CLAUDE.md as `@.fieldkit/KIT.md` (the README covers setup). Repo-specific conventions, setup, and architecture live in the consumer repo's own docs - where the two conflict, flag it briefly before proceeding.

## Always-on

- Act-then-show by default: make the change, surface it, correct after. Ask first for the actions the table marks that way, for anything else outward-facing or irreversible, and for a genuinely new convention or design decision - that last one is gated even when the change itself is local.
- Git and GitHub actions go through the `push`, `pr`, and `merge` skills - don't reach for `git commit`, `git push`, `gh pr create`, or `gh pr merge` directly, even mid-task and even when the step looks trivial. Read-only inspection (`git status`, `git diff`, `git log`) stays direct, as do actions no skill covers - read the matching doc below for those.

| Action                                     | Approval      | Notes                                                          |
| ------------------------------------------ | ------------- | -------------------------------------------------------------- |
| Committing and pushing                     | act-then-show | each coherent piece as it lands, not one batch per session     |
| Force-pushing a branch with an open PR     | ask first     | even when git.md's checks show nothing would be lost           |
| Revising an open PR's title/body           | act-then-show | keep it true as the branch grows                               |
| Filing an issue                            | ask first     | unless the user asked for one                                  |
| Commenting on an issue, editing either     | act-then-show | surface what was filed so it can be corrected                  |
| Closing an issue                           | ask first     | except the automatic close of a `Closes #X` PR on merge        |
| Creating a branch off a non-default branch | ask first     | explain why first; off the default branch it needs no approval |
| Opening a PR                               | ask first     | unless the user typed `/pr`                                    |
| Merging                                    | ask first     | unless the user typed `/merge`; also conditioned on CI         |

- Approval settles whether to act, not what the draft says: once given - a yes, or the `/pr`, `/merge` or issue request itself - draft it and go straight to it.
- An issue settles that a finding is handled later and separately, which forecloses doing it now on the branch in hand. Say what the issue would say, and file it on a yes.
- Merging also needs CI: a failed check or a conflict stops it (report that, don't merge around it), a running check is waited out, a green one merges with no further sign-off.
- A change (see `conventions/specs.md`) carries three approvals of its own. Being asked to plan one is the approval to file its issue. Approving the plan is the approval to create its stage issues. And the PR a stage opens at its gate needs none - one per stage, and opening it is part of reaching the gate. Each stage's merge is gated like any other, and closing a change stays ask-first.
- Commit onto the branch you're already on, even if its existing work looks unrelated.
- A gate on a *follow-up* never holds the action before it: land the push, then ask.
- Route anything learned that's worth keeping by scope: generic cross-repo lessons into the shared conventions kit, repo-specific ones into that repo's own docs.
- `conventions/*.md` are read by humans too: state git/GitHub mechanics as plain facts, and keep this file's process vocabulary (act-then-show, gate, dispatching a subagent) here or in the skill/agent files that execute it, so a convention reads without `KIT.md` open.
- Fix the underlying issue before reaching for a suppression (`# type: ignore`, `# noqa`, tool exclusion). Suppress only when the tool is wrong about the file's context (e.g. a generated or vendored file).
- Delegate to a subagent for context isolation - keeping large, throwaway exploration out of the main window - not for a cheaper model on a small task. A fresh subagent re-pays context from scratch, which dominates a small task's cost.
- A count, or a claim about a file's contents, is re-derived from the tree as it is written into an ADR, spec, issue or commit message - never recalled, never carried over from an older document. Stale figures get repeated precisely because they are already written down.
- Reading part of a file is not reading it. "This document never addresses X", drawn from a head-and-tail skim, is a claim about the part that was not read.

### Linting and formatting

- Don't run formatters or linters unless asked, for code or docs alike - the human runs these and CI enforces them, and a style slip reaching CI is the accepted cost of not burning tokens on lint churn. Match the surrounding style by eye, leaving line lengths and wrapping to CI.
- Do run tests, for correctness feedback: the repo's canonical command with quiet, short-traceback flags, failing fast on the narrowest relevant selection while iterating, then the full suite before declaring work done.

### Reviewing and auditing

- A green CI/lint pass confirms only machine-enforced rules; audit conventions enforced by review (ordering, spacing, doc accuracy) by hand against the diff.
- When a branch introduces or changes a convention, audit existing code for violations and bring any docs that still teach the old pattern into line.
- When editing a file, fix pre-existing convention violations in that file as part of the change; don't extend them. If the fix would span modules, file an issue instead.
- An artifact edited many times needs reading end to end, as a document, before it is called finished. Every edit can be correct while the whole stops describing itself - the usual symptom is a stated goal the body has outgrown. A separate pass from auditing the diff, and it comes last.
- Auditing prose for a phrase needs the text unwrapped first - hard-wrapped Markdown splits phrases across lines, where a line-based `grep` misses them and reports the file clean. Normalise whitespace before matching (e.g. read the file and `' '.join(text.split())`), and treat a no-hit result from a line-based search over wrapped prose as unproven, not as absence.

## Load on Demand

Read the matching file before the action, and only then. The `push`, `pr`, and `merge` skills read `git.md`/`github.md` themselves, so the actions they cover need no row here.

<!-- Read-tool targets (not @-imports). Paths are relative to the consumer
repo root - the directory the session is started from. Read
.fieldkit/conventions/<file> from there, via the .fieldkit symlink. -->

| Before...                                                                       | Read                               |
| ------------------------------------------------------------------------------- | ---------------------------------- |
| A git action `push`/`pr`/`merge` don't cover (rebase, tag, amend)               | .fieldkit/conventions/git.md       |
| A GitHub action `pr`/`merge` don't cover (issues, comments, PR edits)           | .fieldkit/conventions/github.md    |
| Writing an issue, ADR, spec or convention doc, or an exemption list             | .fieldkit/conventions/records.md   |
| Recording a design decision (ADR)                                               | .fieldkit/conventions/decisions.md |
| Planning or building a change, or deciding whether work is one                  | .fieldkit/conventions/specs.md     |
| Building a feature that calls an LLM                                            | .fieldkit/conventions/ai.md        |
| Writing or editing a CI workflow, or a check or lint recipe                     | .fieldkit/conventions/ci.md        |
