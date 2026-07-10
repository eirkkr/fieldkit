---
name: merge
description: Merge the current branch's pull request via squash merge
---

# Merge a pull request via a delegated agent

Launch the `merge-prep` subagent (`subagent_type: merge-prep`) in the
foreground. Relay its mergeability status and draft squash message.

Wait for approval before merging.

Once approved, push (squash merge uses remote state) and run `gh pr merge
--squash` with the approved subject and body.

After it merges, clean up locally: switch to the default branch (`gh repo
view --json defaultBranchRef -q .defaultBranchRef.name`), force-delete the
now-merged branch (`git branch -D <branch>` - squash merges aren't recognized
as merged by plain `-d`), and `git pull --prune`.
