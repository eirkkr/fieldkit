---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push

Decide, from context in hand plus `conventions/git.md`'s branch and commit rules (run `git status`/`git diff` if needed):

- branch name: a new `type/short-description` if on the default branch, else the current branch
- commit message
- exact list of files to stage

If the branch has an open PR (`gh pr view --json number,url,title,body`), check its description against what you're about to push, including `Closes #X` for an issue the push finishes. If stale, draft a revised title/body, keeping the human's wording where it still holds. `$ARGUMENTS`, if given, is extra context.

Then run it, in this turn:

1. `git status`. Unexpected tree (mid-merge, files touched outside the list, unrelated change mixed in): stop and ask.
2. On the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`): create and switch to the new branch.
3. Stage exactly the listed files by name, never `git add -A` or `.`.
4. Commit with the message via heredoc, keeping its line breaks.
5. Push, with `-u origin <branch>` on the branch's first push.
6. PR description needed revising: apply with `gh pr edit`. Fails on token scopes (`read:org`): `gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@<file>`.
7. Stop. Opening a PR and merging are their own skills.

Report the commit (short hash and subject), the branch, whether the push succeeded, and any PR edit made.
