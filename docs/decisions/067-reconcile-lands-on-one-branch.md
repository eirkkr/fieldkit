# 067 - Reconcile lands everything on one branch

## Decision

`/kit-reconcile` puts all its work on its one reconcile branch and PR, and asks only when something bigish comes up.

- The kit checkout's `ref:` in the consumer's workflows is pinned or raised to the commit being reconciled to, in the same PR as the marker bump.
- A small violation fix (KIT.md's definition) is its own commit on that branch, named in the PR description. It gets no separate issue or branch.
- A bigish follow-up, meaning one that spans modules, needs a design call or would bloat the PR's review, stops the run to ask: fold it in, file an issue, or skip it.
- The skill edits first and shows the result, instead of asking approval before editing.

## Reason

The pin is derived from the marker: both are the kit commit reconciled to. Filing an issue to raise it cost more than the one-line edit, and left the repo behind until someone acted on the issue. The old default ("file an issue for each codebase finding") contradicted [ADR 059](059-small-findings-are-fixed-in-place.md), which fixes small findings in place.

Alternatives rejected:

- **Keep the pin as a reported issue.** Raising a pin is a human decision for most CI pins, but not for this one: the kit checkout exists to run the kit's scripts at the version being reconciled.
- **Fix everything on the branch.** A large sweep buried in a marker-bump PR is hard to review and to revert.

## Consequences

- Extends [ADR 012](012-reconcile-marker.md) and [ADR 040](040-reconcile-verifies-references.md): reconcile still audits instructions first, but now also edits one CI line and may fix small code violations. Other human-facing tooling is still left alone.
- A reconcile PR can be larger than a marker bump, with each fix in its own commit so it can be reverted alone.
