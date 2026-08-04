---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push via a delegated agent

Launch the `commit-push` subagent (`subagent_type: commit-push`) in the
foreground, passing `$ARGUMENTS` as its brief. Relay its report.

If the branch has an open PR and the agent reports the description has gone
stale, surface its draft revision and wait for approval. Once approved, apply
it with `gh pr edit`.
