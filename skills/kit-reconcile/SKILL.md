---
name: kit-reconcile
description: Reconcile this repo to the latest shared-conventions-kit changes
argument-hint: "[N | latest]"
disable-model-invocation: true
---

# Reconcile this repo to the latest kit changes

The shared conventions kit (imported here via `@.fieldkit`) has changed. This
command catches this repo up: it checks this repo's references into the kit
still resolve, works out which kit commits are new, reconciles this repo's
agent-facing docs and tooling to them, and advances a stored marker so the next
run knows where it left off.

## Verify the references into the kit resolve

Do this first, whatever the range below resolves to. A stale instruction still
loads and quietly says the wrong thing; a reference that no longer resolves
doesn't load at all, so the session runs with rules missing rather than wrong -
and this session is the least likely to notice, since the failed import is what
would have told it how to behave. References also break from a kit commit the
marker has already passed, or from a local edit, and neither shows up in the
range.

From this repo's root, check:

1. **The symlink.** `test -e .fieldkit/KIT.md`.
2. **The imports.** Every `@.fieldkit/...` line in `CLAUDE.md`, and in anything
   it imports in turn, names a file that exists.
3. **The mentions.** Every other `.fieldkit/...` path in a tracked file -
   READMEs, scripts, `.claude/` config. One `grep -rn '\.fieldkit/'` covers it.
4. **The wiring.** Links into the kit that now dangle (`find . -xtype l`, plus
   `.git/hooks/pre-commit`, which `find` won't reach). `.claude/skills/` and
   `openspec/schemas/` are linked file by file, so a kit-side rename breaks
   them.

Fix each unresolved reference here rather than reporting it onward - usually a
one-line path change. `git -C .fieldkit log --diff-filter=DR --name-status --
<old-path>` finds where the target moved; if it was removed rather than moved,
drop the reference and say so. For a dangling link, re-run the matching
`.fieldkit/scripts/enable-*.sh` rather than re-pointing it by hand.

## Resolve the range

The marker file `.fieldkit-rev` at this repo's root records the kit commit this
repo was last reconciled to as a bare SHA. The kit squash-merges, so each
commit on its `main` is one change. Resolve the range from `$ARGUMENTS`:

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
whether it has codebase implications. File a narrow issue for each one that
does, then list what was filed. Don't sweep the code here; that's a separate
job.

## Advance the marker and open the PR

Set `.fieldkit-rev` to the kit HEAD you reconciled to
(`git -C .fieldkit rev-parse main`) and commit the bump alongside the reconcile
edits. This also creates the file on a repo that had no marker yet. If the
audit found nothing to change, still bump the marker and open a marker-only PR -
that records the repo was checked up to this commit.

Follow the kit's git conventions: show me the proposed changes for approval
before editing, work on a branch, and open a PR.
