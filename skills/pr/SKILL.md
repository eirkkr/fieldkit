---
name: pr
description: Draft and open a pull request for the current branch
argument-hint: "[short summary of the change, optional]"
---

# Open a pull request via a delegated agent

Launch the `pr-prep` subagent (`subagent_type: pr-prep`) in the foreground,
passing `$ARGUMENTS` as context if given. Relay its draft (compare link,
title, body).

Wait for approval - opening a PR asserts the branch is ready for review.

Once approved, run `gh pr create` with the approved title and body.
