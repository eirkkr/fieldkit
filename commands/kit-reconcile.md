---
description: Reconcile this repo to the latest shared-conventions-kit changes
argument-hint: "[git range, e.g. main~3..main]"
---

The shared conventions kit (imported here via `@.fieldkit`) has changed. See
what changed: review the kit's recent history with `git -C .fieldkit log` and
`git -C .fieldkit show <commit>`. It squash-merges, so the latest commit on main
is the change. If a range is given below, use it instead of the latest commit to
catch up several changes at once.

Range: $ARGUMENTS

Then reconcile this repo to the current kit conventions:

1. Audit agent-facing docs and instructions for anything that now contradicts
   the kit, and bring them into line.
2. Make any repo-side change the new rules imply - commands, recipes, config.
3. Leave human-facing tooling alone: don't touch CI, pre-commit, or the linters
   themselves. This reconciles agent instructions, not the human's tools.

Follow the kit's git conventions: show me the proposed changes for approval
before editing, work on a branch, and open a PR.
