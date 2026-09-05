# GitHub and external actions

- Filing an issue is confirmed first, unless the person asked for one - that
  request is the approval, and the issue is drafted and filed straight
  through. What is being approved is that the issue should exist, not its
  wording: the draft needs no review, and a filed issue is edited in place if
  it missed.
- Commenting on an issue, and editing either an issue or a comment, need no
  prior approval - do it, then show what was written so it can be corrected.
  Closing an issue is confirmed first: it ends a thread someone may still be
  relying on. The close a merge performs is already covered - merging a PR
  whose body carries `Closes #X` closes `X` automatically, and the approval to
  merge is the approval to close.
- PRs: mechanics live in [git.md](git.md). Once open, keep the title
  and body in sync as the branch grows - revise it directly when it drifts,
  keeping the human's own wording where it still holds. The description is
  what reviewers read and what the squash message is built from, so it's
  worth getting right.
- Before filing an issue, check for duplicates/broader scope:
  `gh issue list --search "<2-3 keywords>"`.
- Out-of-scope work doesn't get bundled into the branch in hand. The two ways
  out are a narrow issue or doing it now on its own branch, and which one
  applies depends on things only the person asking knows - what else is
  queued, how much scope there is appetite for today. So the finding gets
  described and the choice put to them, rather than an issue filed and the
  question closed.
- In a public repo, don't name a private one. Issue text, PR descriptions,
  comments, and commit messages are as public as the code, and a
  `owner/repo#123` cross-reference or a `github.com` URL names it as plainly
  as prose does. Refer to it by role instead - "a consumer repo", "a Python
  consumer". The substance of a worked example - the finding, the numbers, the
  file names - is fine; the repo's identity is what stays out.

## Issues

- Titles: imperative mood, no trailing period, ~72-character soft limit.
  Optionally prefix with the primary component when it adds clarity (e.g.
  `API:`, `Docs:`); the prefix list is per-repo and grows with the codebase.
- Use the bug template for anything broken, the feature template for new
  functionality. File refactors, chores, and docs without a template.
- Keep the description focused on the specific finding - a narrow,
  well-described issue is more actionable than a broad one.
