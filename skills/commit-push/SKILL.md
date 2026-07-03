---
name: commit-push
description: Commit and push the current changes to a branch
argument-hint: "[commit message hint]"
---

# Commit and push via a delegated agent

Launch the `commit-push` subagent (`subagent_type: commit-push`), foreground
since the result is needed immediately. Pass it nothing beyond any commit
message hint from `$ARGUMENTS` - it works the rest out itself by running
commands.

Relay its report (branch name, commit SHA/subject, push status) to the
user - don't just say "done."
