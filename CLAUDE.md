# Claude Guidance (Generic)

Shared dev conventions for use across repos. A consumer repo pulls these in by
`@`-importing this file (or individual `conventions/*` files) from its own
CLAUDE.md via a `.fieldkit` symlink to this repo - e.g. `@.fieldkit/CLAUDE.md`.
See the README for the one-time symlink setup.

- If a request would produce output that conflicts with these conventions, flag
  it briefly before proceeding rather than silently complying.
- These are the generic, cross-repo rules. Repo-specific conventions, setup, and
  architecture live in the consumer repo's own docs.

## Load Always

@conventions/workflow.md
@conventions/git.md

## Load on Demand

Situational conventions, not carried in context. Read the matching file before
the action; don't load it otherwise.

Critical even before reading: gate only on what's outward-facing or
irreversible - get approval before creating or editing an issue or comment,
opening a PR, or merging. Local pre-merge work (branches, edits, commits, branch
pushes) is act-then-show: do it, surface it, correct after.

<!-- Read-tool targets (not @-imports). Paths are relative to the consumer
repo root - the directory the session is started from. Read
.fieldkit/conventions/<file> from there, via the .fieldkit symlink. -->

| Before...                                          | Read                                        |
| -------------------------------------------------- | ------------------------------------------- |
| Any GitHub action (issue, PR, comment)             | .fieldkit/conventions/github.md             |
| Recording a design decision (ADR)                  | .fieldkit/conventions/decisions.md          |
| Writing an implementation spec or plan             | .fieldkit/conventions/specs.md              |
| Building a feature that calls an LLM               | .fieldkit/conventions/ai.md                 |
| Invoking Python in any form (script, inline, call) | .fieldkit/conventions/python/run.md         |
