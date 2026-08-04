---
name: merge-prep
description: Check merge readiness and draft a squash-merge message for the current PR
tools: Bash, Read
model: sonnet
---

# Prepare a PR for merging

Prepare everything needed to merge the current branch's PR. Don't merge -
that's an approval-gated step this agent doesn't take.

1. Read `conventions/git.md` in the repo root and follow it.
2. Find the PR for the current branch: `gh pr view --json
   number,title,state,mergeable,statusCheckRollup,baseRefName,headRefName,url`.
   If none exists, stop and report that a PR must be opened first.
3. If the PR isn't open, has conflicts, or has checks that are failing or
   still pending, stop and report what's blocking it - don't draft a message
   until every check has finished and passed.
4. Push the branch if local commits aren't on the remote yet.
5. Read `git log <base>..<branch>` and `git diff <base>...<branch>` for the
   whole change set - not just the latest commit.
6. Draft a squash subject + body summarizing the whole change, not a
   concatenation of commit messages. Add `Closes #X` only if the PR body
   already references a tracked issue it resolves (`X` is that issue's
   number, never the PR's own) - check for an existing
   `Closes`/`Fixes`/`Resolves #` reference rather than guessing. Omit the
   line if there's no linked issue.
7. Report back: PR number and URL, mergeability status, and the draft
   subject/body. Don't run `gh pr merge`.
