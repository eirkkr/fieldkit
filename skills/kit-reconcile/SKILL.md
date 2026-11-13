---
name: kit-reconcile
description: Reconcile this repo to the latest shared-conventions-kit changes
argument-hint: "[N | latest]"
disable-model-invocation: true
---

# Reconcile this repo to the latest kit changes

The shared conventions kit (imported via `@.fieldkit`) has changed; this command catches this repo up, in the order below.

## Verify the references into the kit resolve

Do this first, whatever the range resolves to. A dangling reference loads nothing: the session runs with rules silently missing. References also break from a kit commit the marker already passed, or a local edit; neither shows in the range.

From this repo's root, check:

1. **The symlink.** `test -e .fieldkit/KIT.md`.
2. **The imports.** Every `@.fieldkit/...` line in `CLAUDE.md`, and in anything it imports in turn, names a file that exists.
3. **The mentions.** Every other `.fieldkit/...` path in a tracked file (READMEs, scripts, `.claude/` config). One `grep -rn '\.fieldkit/'` covers it.
4. **The wiring.** Links into the kit that now dangle (`find . -xtype l`, plus `.git/hooks/`, which `find` won't reach). `.claude/skills/` is linked file by file, so a kit-side rename breaks it.
5. **The CI callers.** Every `uses: <kit-repo>/.github/workflows/<file>@...` in `.github/workflows/` names a file existing at `.fieldkit/.github/workflows/<file>`. A missing one fails every PR.

Fix each unresolved reference here, usually a one-line path change. `git -C .fieldkit log --diff-filter=DR --name-status -- <old-path>` finds where the target moved; removed: drop the reference or link and say so. Dangling link or CI caller naming a missing workflow: re-run the matching `.fieldkit/scripts/enable-*.sh` instead of editing by hand (`enable-pr-checks.sh` replaces a caller an earlier version wrote).

Then re-run every `enable-*.sh` this repo has already run (its links or files are present), even where nothing dangles: each is idempotent, and a kit change can add to what one installs (`enable-hooks.sh` gaining `commit-msg` reaches no clone until re-run). Enabling one the repo never ran is the human's call.

Then check the workflows running the kit's scripts. For each `actions/checkout` step in `.github/workflows/` whose `repository:` matches this repo's kit (`owner/name` from `git -C .fieldkit remote get-url origin`): a `ref:` of 40 hex characters is a pin; a branch, a tag or no `ref:` is an unpinned checkout, which `conventions/ci.md` ("Pin everything a workflow runs on") rules out. For a pin, count how far behind the kit's `main` it is with `git -C .fieldkit rev-list --count <pin>..main`; unmeasured if the pin is not in the local clone. Then pin or raise each to the kit commit being reconciled to (`git -C .fieldkit rev-parse main`, the SHA the marker gets): kit wiring, same as the marker. Edit only that `ref:`; other CI pins are not this skill's. Report each by file: before, after, distance.

## Resolve the range

`.fieldkit-rev` at this repo's root holds the kit commit last reconciled to, a bare SHA. The kit squash-merges, so each commit on its `main` is one change. Resolve the range from `$ARGUMENTS`:

- **No argument, marker present:** `<marker-sha>..main`, every kit commit since the last reconcile.
- **No argument, marker absent:** the latest kit commit only. Warn that `.fieldkit-rev` is missing, so older changes were not reviewed.
- **A number `N`:** `main~N..main`, the last N kit commits.
- **`latest`:** the latest kit commit only.

Read the kit history for that range with `git -C .fieldkit log main` and `git -C .fieldkit show <commit>`.

## Reconcile this repo

1. Audit agent-facing docs and instructions for anything now contradicting the kit; bring them into line.
2. Make any repo-side change the new rules imply: commands, recipes, config.
3. Leave other human-facing tooling (CI, pre-commit, linters) alone. Exceptions, both kit wiring kept current in the references step: what the kit's `enable-*.sh` scripts wrote (links, hooks, CI caller workflows), and the kit checkout's `ref:` pin.

## Codebase follow-ups

The steps above reconcile *instructions*, not the *codebase*. For each changed convention in range, judge whether existing code now violates it.

A violation fix that is *small* (KIT.md's definition) goes on the reconcile branch as its own commit, named in the PR description. The CI pin is one.

Anything not small is *bigish*: stop and ask: fold in, file an issue (title and finding in a sentence), or skip. Sweeping the whole codebase stays a separate job.

## Advance the marker and open the PR

Set `.fieldkit-rev` to the kit HEAD reconciled to (`git -C .fieldkit rev-parse main`), creating it if absent; commit the bump with the reconcile edits. Nothing to change: still open a marker-only PR, recording the repo was checked up to this commit.

Follow the kit's git conventions: work on one reconcile branch, open a PR. Act-then-show: make the edits, then show what changed; no approval before editing. Ask first only for a bigish follow-up (above).
