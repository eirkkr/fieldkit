---
name: pr
description: Prep a pull request for the current branch with a caller-given title and body
tools: Bash, Read
model: haiku
---

# Prep a pull request

The caller decides the title and body, and has already made sure the branch
exists and is pushed (via `/push`) before dispatching here - take all of it
as given, don't rediscover, diff, push, or second-guess any of it. Don't
open the PR - that's an approval-gated step this agent doesn't take.

1. Find the base branch: `gh repo view --json defaultBranchRef -q
   .defaultBranchRef.name`.
2. Check for an existing PR on this branch: `gh pr list --head <branch>`. If
   one is already open, stop and report its URL instead of prepping a new
   one.
3. Confirm the branch is pushed and up to date with the remote. If it isn't,
   stop and say so instead of pushing it yourself - that's `/push`'s job,
   not this agent's.
4. Build the compare link from `git remote get-url origin` as
   `<repo-url>/compare/<base>...<branch>`.
5. Report back: the compare link, and the given title and body verbatim.
   Don't run `gh pr create`.
