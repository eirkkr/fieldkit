# Claude Guidance (Generic)

Shared dev conventions for use across repos. A consumer repo pulls these in by
`@`-importing this file (or individual `conventions/*` files) from its own
CLAUDE.md - e.g. `@~/src/fieldkit/CLAUDE.md`.

- If a request would produce output that conflicts with these conventions, flag
  it briefly before proceeding rather than silently complying.
- These are the generic, cross-repo rules. Repo-specific conventions, setup, and
  architecture live in the consumer repo's own docs.

## Load Always

@~/src/fieldkit/conventions/workflow.md
@~/src/fieldkit/conventions/git.md
@~/src/fieldkit/conventions/style.md

## Load on Demand

Situational conventions, not carried in context. Read the matching file before
the action; don't load it otherwise.

Critical even before reading: get approval before creating or editing an issue
or comment, marking a PR ready for review, or merging. Creating and updating
draft PRs needs no pre-approval.

| Before...                              | Read                                    |
| -------------------------------------- | --------------------------------------- |
| Any GitHub action (issue, PR, comment) | ~/src/fieldkit/conventions/github.md    |
| Recording a design decision (ADR)      | ~/src/fieldkit/conventions/decisions.md |
