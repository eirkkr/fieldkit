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

Critical even before reading: never take an externally-visible GitHub action
(issue, PR, comment) without showing a draft and waiting for approval.

| Before...                              | Read                                    |
| -------------------------------------- | --------------------------------------- |
| Any GitHub action (issue, PR, comment) | ~/src/fieldkit/conventions/github.md    |
| Recording a design decision (ADR)      | ~/src/fieldkit/conventions/decisions.md |

## Language-specific (opt-in)

For Python repos, also import `@~/src/fieldkit/conventions/python.md` from your
CLAUDE.md.
