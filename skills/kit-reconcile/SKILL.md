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

Do this first, and whatever the range resolves to below. A stale instruction
still loads and quietly says the wrong thing; a reference that no longer
resolves doesn't load at all, so the session runs with rules missing rather
than wrong - and the session least likely to notice is this one, since the
unresolved import is exactly what would have told it how to behave. A reference
can also break from a kit commit the marker has already passed, or from a local
edit; neither shows up in the range.

Check, from this repo's root:

1. **The symlink.** `.fieldkit` resolves, and what it points at is a kit
   checkout - `test -e .fieldkit/KIT.md`.
2. **The imports.** Every `@.fieldkit/...` line in this repo's `CLAUDE.md`, and
   in anything it imports in turn, names a file that exists.
3. **The mentions.** Every other `.fieldkit/...` path named in a tracked file -
   READMEs, repo docs, scripts, `.claude/` config. These don't break a session
   the way an unresolved import does, but they're the same one-line fix and the
   whole sweep is one `grep -rn '\.fieldkit/'` over tracked files.
4. **The wiring.** Symlinks that point into the kit and now dangle
   (`find . -xtype l`, plus `.git/hooks/pre-commit` on a repo that opted into
   the hook, since `.git` isn't searched). `.claude/skills/` and
   `openspec/schemas/` are linked file by file, so a kit-side rename leaves
   them broken.

Every unresolved reference is a finding to fix in this run, not a warning to
pass on. The fix is usually a one-line path change: find where the target moved
to with `git -C .fieldkit log --diff-filter=DR --name-status -- <old-path>` and
correct the path. If it was removed rather than moved, drop the reference and
say what was dropped. For a dangling link under `.claude/skills/` or
`openspec/schemas/`, re-run the matching `.fieldkit/scripts/enable-*.sh` rather
than re-pointing links by hand.

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
