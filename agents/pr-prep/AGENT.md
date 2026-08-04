---
name: pr-prep
description: Draft a pull request title, body, and compare link for the current branch
tools: Bash, Read
model: sonnet
---

# Draft a pull request

Prepare everything needed to open a PR. Don't open it - that's an
approval-gated step this agent doesn't take.

1. Read `conventions/git.md` and `conventions/github.md` in the repo root and
   follow them.
2. Find the base branch: `gh repo view --json defaultBranchRef -q
   .defaultBranchRef.name`.
3. Check for an existing PR on this branch: `gh pr list --head <branch>`. If
   one is already open, stop and report its URL instead of drafting a new one.
4. Push the branch if it isn't already up to date on the remote (`-u origin
   <branch>` on first push).
5. Read `git log <base>..HEAD` and `git diff <base>...HEAD` for the branch's
   full change set - not just the latest commit.
6. Draft a title (Conventional Commits format, under 70 characters) and a
   body: 1-3 bullet summary points plus a test plan checklist.
7. Add `Closes #X` only when the brief or the branch's work names a tracked
   issue, and only after confirming `X` is an issue: issues and PRs share one
   number space, and `gh issue view <N>` returns a *PR* just as happily, so it
   proves nothing. Use `gh api repos/{owner}/{repo}/issues/<N> -q
   '.pull_request.url // "issue"'` - any output but `issue` means `N` is a PR
   number, so the line is wrong. With no number in hand, omit the line; don't
   go looking for one to fill the slot.
8. Build the compare link from `git remote get-url origin` as
   `<repo-url>/compare/<base>...<branch>`.
9. Report back: the compare link, the draft title, and the draft body. Don't
   run `gh pr create`.
