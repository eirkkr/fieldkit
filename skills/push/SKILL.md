---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push via a delegated agent

Decide, from context already in hand plus `conventions/git.md`'s branch and
commit conventions - run `git status`/`git diff` yourself if you need them to
pin this down:

- the branch name (a new `type/short-description` if the current branch is
  the default branch, otherwise the current branch)
- the commit message
- the exact list of files to stage

If the branch already has an open PR (`gh pr view --json
number,url,title,body`), check whether its description still describes what
you're about to push - you already have the diff for this, no need to wait
for the push. If it's gone stale, draft a revised title/body (keeping the
human's own wording where it still holds) - no approval needed, this is
act-then-show like the rest.

Launch the `push` subagent (`subagent_type: push`) in the foreground with the
branch, commit message, and file list, plus `$ARGUMENTS` for whatever extra
context was given, plus the revised title/body to apply if the PR needed
one. The agent takes all of this as given; it doesn't rediscover, diff, or
second-guess any of it. Relay its report.
