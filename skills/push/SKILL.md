---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push

Decide, from context in hand plus `conventions/git.md`'s branch and commit rules (run `git status`/`git diff` if needed):

- branch name: the current branch, unless it is the default branch or breaks git.md's branch-name rules (`worktree-<name>` from a worktree Claude Code made itself, a sub-agent's or `claude --worktree`'s; a branch the creation script made already conforms): then a new `type/short-description`, reusing `<name>` where it fits
- commit message
- exact list of files to stage

If the branch has an open PR (`gh pr view --json number,url,title,body`), check its description against what you're about to push, including `Closes #X` for an issue the push finishes. If stale, draft a revised title/body, keeping the human's wording where it still holds. `$ARGUMENTS`, if given, is extra context.

Then run it, in this turn:

1. `git status`. Unexpected tree (mid-merge, files touched outside the list, unrelated change mixed in): stop and ask.
2. Branch name needs changing:
   - on the default branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`): the edits are in this checkout and a worktree would leave them behind. Create and switch to the new branch here, not in a worktree.
   - on a branch that breaks the rules, no remote branch yet (`git ls-remote --exit-code --heads origin <branch>` fails): `git branch -m <new name>`.
   - on a branch that breaks the rules and is pushed: stop and ask, a rename would orphan the remote branch.
3. Stage exactly the listed files by name, never `git add -A` or `.`.
4. Commit with the message via heredoc, keeping its line breaks.
5. Push, with `-u origin <branch>` on the branch's first push.
6. PR description needed revising: apply with `gh pr edit`.
7. Stop. Opening a PR and merging are their own skills.

Report the commit (short hash and subject), the branch, whether the push succeeded, and any PR edit made.
