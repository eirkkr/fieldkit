# Shared conventions

Shared dev conventions for use across repos. A consumer repo pulls these in by
`@`-importing this file (or individual `conventions/*` files) from its own
CLAUDE.md - e.g. `@~/src/fieldkit/CLAUDE.md`.

- If a request would produce output that conflicts with these conventions, flag
  it briefly before proceeding rather than silently complying.
- These are the generic, cross-repo rules. Repo-specific conventions, setup, and
  architecture live in the consumer repo's own docs.

## Always-on

Imported into context, since they bear on nearly every edit and commit.

@~/src/fieldkit/conventions/workflow.md
@~/src/fieldkit/conventions/git.md
@~/src/fieldkit/conventions/style.md

## Load on demand

Situational conventions, not carried in context. Read the matching file before
the action; don't load it otherwise.

Critical even before reading: never create or edit an issue or comment, or merge
a PR, without showing the proposed content for approval first. Creating and
updating PRs themselves needs no pre-approval.

| Before...                              | Read                                    |
| -------------------------------------- | --------------------------------------- |
| Any GitHub action (issue, PR, comment) | ~/src/fieldkit/conventions/github.md    |
| Recording a design decision (ADR)      | ~/src/fieldkit/conventions/decisions.md |
