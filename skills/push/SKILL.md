---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push

Decide, from context in hand plus `conventions/git.md`'s branch and commit rules (run `git status`/`git diff` if needed):

- branch name: the current branch, unless it is the default branch or an unpushed `worktree-*` one (a worktree not yet renamed): then a new `type/short-description`
- commit message
- exact list of files to stage

If the branch has an open PR (`gh pr view --json number,url,title,body`), check its description against what you're about to push, including `Closes #X` for an issue the push finishes. If stale, draft a revised title/body, keeping the human's wording where it still holds. `$ARGUMENTS`, if given, is extra context.

Then run it, in this turn:

1. `git status`. Unexpected tree (mid-merge, files touched outside the list, unrelated change mixed in): stop and ask.
2. Branch name needs changing:
   - on the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`): the work started outside a worktree, and a worktree would leave its changes behind. Create and switch to the new branch here.
   - on an unpushed `worktree-*` branch: `git branch -m <new name>`.
   - on a pushed `worktree-*` branch: stop and ask, a rename would orphan the remote branch.
3. Stage exactly the listed files by name, never `git add -A` or `.`.
4. Commit with the message via heredoc, keeping its line breaks.
5. Push, with `-u origin <branch>` on the branch's first push.
6. PR description needed revising: apply with `gh pr edit`; if it fails with "required scopes" (`read:org`), use `gh api -X PATCH repos/{owner}/{repo}/pulls/<n> -F body=@<file>`.
7. Stop. Opening a PR and merging are their own skills.

Report the commit (short hash and subject), the branch, whether the push succeeded, and any PR edit made.
