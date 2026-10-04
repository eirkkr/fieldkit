---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push

Decide, from context already in hand plus `conventions/git.md`'s branch and commit conventions - run `git status`/`git diff` yourself if you need them to pin this down:

- the branch name (a new `type/short-description` if the current branch is the default branch, otherwise the current branch)
- the commit message
- the exact list of files to stage

If the branch has an open PR (`gh pr view --json number,url,title,body`), check its description against what you're about to push, including a `Closes #X` for an issue the push finishes. If it's gone stale, draft a revised title/body, keeping the human's own wording where it still holds. `$ARGUMENTS`, if given, is extra context for these decisions.

Then run it, in this turn:

1. `git status`. If the tree looks unexpected - mid-merge, files touched outside the list, an unrelated change mixed in - stop and ask.
2. If the current branch is the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), create and switch to the new branch.
3. Stage exactly the listed files by name - never `git add -A` or `.`.
4. Commit with the message, passed through a heredoc so it keeps its line breaks.
5. Push, with `-u origin <branch>` on the branch's first push.
6. If the PR description needed revising, apply it with `gh pr edit`.
7. Stop there - opening a PR and merging are their own skills.

Report the commit (short hash and subject), the branch, whether the push succeeded, and any PR edit made.
