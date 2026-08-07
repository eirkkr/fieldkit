---
name: push
description: Commit and push the current repo's pending changes to a branch
tools: Bash, Read
model: haiku
---

# Commit and push pending changes

The caller decides the branch name, commit message, file list, and - if
there's a PR to touch - how to update it. Take all of this as given; don't
rediscover, diff, or second-guess any of it.

1. Run `git status`. If the tree looks unexpected (mid-merge, files touched
   outside the given list, an unrelated change mixed in), stop and ask.
2. If the current branch is the repo's default branch (`gh repo view --json
   defaultBranchRef -q .defaultBranchRef.name`), create and check out the
   given branch.
3. Stage exactly the given files by name (no `-A`/`.`).
4. Commit with the given message.
5. Push the branch (`-u origin <branch>` on first push).
6. If given an exact PR title/body to apply, run `gh pr edit` with them. If
   only told a PR is open with no edit instructions, leave it alone - just
   carry the link through to the report.
7. Don't open a PR or merge - stop after pushing.
8. Report back a branch link (`git remote get-url origin` →
   `<repo-url>/tree/<branch>`), push status, and PR-edit status if step 6
   applied one.
