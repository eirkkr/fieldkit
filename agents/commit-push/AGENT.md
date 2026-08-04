---
name: commit-push
description: Commit and push the current repo's pending changes to a branch
tools: Bash, Read
model: sonnet
---

# Commit and push pending changes

Don't assume - verify by running commands.

1. Read `conventions/git.md` in the repo root and follow it.
2. Run `git status` and `git diff --stat` (staged and unstaged).
3. If the tree looks unexpected (mid-merge, unrelated changes mixed in), stop
   and ask.
4. If the current branch is the repo's default branch (`gh repo view --json
   defaultBranchRef -q .defaultBranchRef.name`), create and check out a new
   branch first - `type/short-description` per `conventions/git.md`, inferring
   the type and description from the change unless a name is given in the
   brief.
5. Write the commit message from a given hint or summary if provided,
   otherwise `git diff` only the files whose purpose isn't clear from their
   names and the stat.
6. Stage only the relevant files by name (no `-A`/`.`).
7. Push the branch (`-u origin <branch>` on first push).
8. If the branch already has an open PR (`gh pr view --json
   number,url,title,body`), check its description still describes what's now
   on the branch - new commits routinely add scope the body never mentions.
   If it's gone stale, draft a revised body (keeping the human's own wording
   where it still holds) and include it in the report for approval. Don't run
   `gh pr edit` yourself.
9. Don't open a PR or merge - stop after pushing.
10. Report back a branch link (`git remote get-url origin` →
    `<repo-url>/tree/<branch>`), push status, and the PR-body draft if step 8
    produced one.
