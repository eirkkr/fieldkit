---
description: Reconcile this repo to the latest shared-conventions-kit changes
argument-hint: "[N | latest]"
---

# Reconcile this repo to the latest kit changes

The shared conventions kit (imported here via `@.fieldkit`) has changed. This
command catches this repo up: it works out which kit commits are new, reconciles
this repo's agent-facing docs and tooling to them, and advances a stored marker
so the next run knows where it left off.

## Resolve the range

The marker file `.fieldkit-rev` at this repo's root records the kit commit this
repo was last reconciled to as a bare SHA. The kit squash-merges, so each commit on
its `main` is one change. Resolve the range from `$ARGUMENTS`:

- **No argument, marker present:** `<marker-sha>..main` - every kit commit since
  the last reconcile.
- **No argument, marker absent:** the latest kit commit only. Warn that
  `.fieldkit-rev` is missing, so older changes were not reviewed.
- **A number `N`:** `main~N..main` - the last N kit commits.
- **`latest`:** the latest kit commit only.

Read the kit history for that range with `git -C .fieldkit log main` and
`git -C .fieldkit show <commit>`.

## Reconcile this repo

1. Audit agent-facing docs and instructions for anything that now contradicts
   the kit, and bring them into line.
2. Make any repo-side change the new rules imply - commands, recipes, config.
3. Leave human-facing tooling alone: don't touch CI, pre-commit, or the linters
   themselves. This reconciles agent instructions, not the human's tools.

## Surface codebase follow-ups

The steps above reconcile *instructions*, not the *codebase*. Some convention
changes also imply source edits this command does not make - a style or language
rule the existing code now violates. For each changed convention in range, judge
whether it has codebase implications. List the ones that do and ask me whether to
file an issue for each before creating any. Don't sweep the code here; that's a
separate job.

## Advance the marker and open the PR

Set `.fieldkit-rev` to the kit HEAD you reconciled to
(`git -C .fieldkit rev-parse main`) and commit the bump alongside the reconcile edits. This also creates
the file on a repo that had no marker yet. If the audit found nothing to change,
still bump the marker and open a marker-only PR - that records the repo was
checked up to this commit.

Follow the kit's git conventions: show me the proposed changes for approval
before editing, work on a branch, and open a PR.
