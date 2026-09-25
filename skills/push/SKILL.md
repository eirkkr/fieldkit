---
name: push
description: Commit and push the current changes to a branch
argument-hint: "[short summary of what changed and why]"
---

# Commit and push

Decide, from context already in hand plus `conventions/git.md`'s branch and
commit conventions - run `git status`/`git diff` yourself if you need them to
pin this down:

- the branch name (a new `type/short-description` if the current branch is
  the default branch, otherwise the current branch)
- the commit message
- the exact list of files to stage

If the branch already has an open PR (`gh pr view --json
number,url,title,body`), check whether its description still describes what
you're about to push - you already have the diff for this. If it's gone
stale, draft a revised title/body (keeping the human's own wording where it
still holds) - no approval needed, this is act-then-show like the rest.
`$ARGUMENTS`, if given, is extra context for these decisions.

Then run it, in this turn:

1. `git status`. If the tree looks unexpected - mid-merge, files touched
   outside the list, an unrelated change mixed in - stop and ask.
2. If the current branch is the default branch (`gh repo view --json
   defaultBranchRef -q .defaultBranchRef.name`), create and switch to the
   new branch.
3. Stage exactly the listed files by name - never `git add -A` or `.`.
4. Commit with the message, passed through a heredoc so it keeps its line
   breaks.
5. Push, with `-u origin <branch>` on the branch's first push.
6. If the PR description needed revising, apply it with `gh pr edit`.
7. Don't open a PR or merge - stop after pushing.

Report the commit (short hash and subject), the branch, whether the push
succeeded, and any PR edit made. The commit lands before the turn ends, so
the `Stop` hook measures formatter drift against it
([ADR 035](../../docs/decisions/035-measure-the-fixer-not-the-transcript.md)).
These steps run here rather than in a subagent
([ADR 045](../../docs/decisions/045-inline-git-skills.md)).
