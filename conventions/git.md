# Git conventions

- Never commit directly to the default branch. Branch, commit there, open a PR. The kit's `pre-commit` hook enforces this once installed (see Hooks and CI checks).

## Branches

- [Conventional Branch](https://conventional-branch.github.io/) naming: `type/short-description`, lowercase, hyphen-separated.
- Allowed prefixes: `feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/`. No others (`refactor/`, `fix/`, `test/`, etc.).
- At most 50 characters, prefix included - a few words of description. The issue or PR carries the detail.
- Branch off the default branch. Branching off another branch is an anti-pattern - it stacks work on something that can still change or get discarded.
- One branch is one unit of work, and for a change planned in stages that unit is the *stage*, not the whole change: each stage gets its own branch off the default branch and merges when its review gate closes ([specs.md](specs.md)). A change spanning five stages is five branches in sequence, each cut from the previous one's merge - never stacked on a branch still under review.

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/): `type: short description`, imperative mood. No scope.
- A breaking change - one a consumer has to act on - is marked with `!` after the type (`feat!: drop the old flag`) and a `BREAKING CHANGE:` line in the body saying what to do. Each requires the other.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`. No others (`ci`, `style`, `perf`, `build`, etc.).
- The description starts lowercase and has no trailing period.
- The subject is at most 72 characters - GitHub cuts longer ones on its commit pages.
- For more context, add a body after a blank line, every line at most 72 characters, so `git log`'s 4-space indent still fits 80 columns. A line that is one unbreakable word - a URL or a path, optionally after a list marker or a `[1]:` label - may run longer, since it can't be wrapped.

## Pull requests and merging

- PR title follows the Commits rules above. It becomes the squash subject once GitHub appends `(#N)`, so the 72 includes that suffix. A `!` title needs a `BREAKING CHANGE:` line in the PR body, which the squash body carries on. No issue numbers in the title.
- `Closes #X` in the PR body references a tracked issue the work resolves - and when there is none, there's simply no such line. A mention in prose closes nothing. A number is never inferred, and never the PR's own: issues and PRs share one number space, so a wrong guess still resolves to something, and `gh issue view <N>` returns a PR just as happily. The check is `gh api repos/{owner}/{repo}/issues/<N> -q '.pull_request.url // "issue"'`, where any output but `issue` means `N` is a PR.
- A sentence about the PR's own state ("unmerged", "in review") turns false at the merge: rewrite it on the branch first.
- Always `git push` before `gh pr merge` (squash merge uses remote state).
- Work in progress stays on the branch: push freely, but open a PR only when the work is ready for review.
- Every push to an open PR's branch must leave its description true: push, check the body against the branch as pushed, and revise it at once if stale ([github.md](github.md)).
- Squash-merge: synthesise a subject + body summarising the whole change; don't concatenate commit messages. Append `(#PR)` to a custom `--subject` manually (GitHub omits it when you provide a custom subject). The footer takes its `Closes #X` lines from both `gh pr view --json closingIssuesReferences -q '.closingIssuesReferences[].number'` and the PR body's closing-keyword lines (`Closes`, `Fixes`, `Resolves`), each number checked as above. GitHub's list can be empty at merge time, and an issue it has not linked stays open, so the footer is what closes it. With neither, omit the line.
- Merge once CI is green and the PR has no conflicts; a red check or unresolved conflicts block it outright, a still-running check is waited out instead. Where a repo uses [Manual CI](ci.md#manual-ci), a `skipping` check is not green.

## Rewriting history

- Rebasing or amending a pushed branch rewrites its commits, so the push after it is a force-push: `--force-with-lease=<branch>:<sha last seen>`, which refuses if anything landed since. Plain `--force`, and a bare `--force-with-lease` (which trusts whatever was last fetched), can overwrite someone else's push.
- A branch rebased locally and never pushed has commits on both sides of its remote, which means neither a conflict nor a safe force-push:
  - `git cherry -v <branch> origin/<branch>` marks each remote commit `-` if the local branch has the same patch, `+` if not. All `-` means nothing would be lost.
  - A `+` can still be a rebased copy: the patch changes when the base changed neighbouring lines or a conflict was resolved. Then `git diff origin/<branch> <copy of the remote tip>` should show only what `git diff <old base> <new base>` does, each base being that side's merge-base with the default branch. Anything more exists only on the remote.
- A force-push that loses nothing still replaces commits the reviewer of an open PR has read or pulled, so they are told first. The lease names the SHA that was checked; if it refuses, check again rather than reaching for `--force`.
- The default branch is never rewritten.
- A rewrite re-SHAs every commit, so anything citing the old SHAs goes stale: a comment that links a commit, and under the `review-gated` OpenSpec schema a stage's review note.

## Hooks and CI checks

- Git hooks, installed once per clone from the repo root with `.fieldkit/scripts/enable-hooks.sh`: `pre-commit` refuses commits on the default branch (from `fieldkit.defaultBranch` git config, else `origin/HEAD`, else `main`; set that config in a repo whose `origin/HEAD` is unset or guessed wrong); `commit-msg` refuses a message breaking the Commits rules (git's own merge, revert, `fixup!` and `squash!` messages pass). A refusal means the commit belongs on a branch or its message needs fixing, so `--no-verify` is never the answer.
- Two Claude Code `PreToolUse` hooks, registered by `just install`, act only in a repo with `.fieldkit` or in the kit, on Claude's Bash commands: one refuses creating or renaming a branch to a name breaking the Branches rules; one checks the squash message passed to `gh pr merge` (Commits rules, plus a `(#N)` suffix matching the PR).
- CI checks each PR's title and branch name. Enable it with `.fieldkit/scripts/enable-pr-checks.sh` and commit the workflow it writes. Bot-opened PRs are exempt, since bots name branches and PRs from their own config.
- All of these enforce constants in the kit's `hooks/conventions.py`, which mirror the Branches and Commits bullets above: a rule change changes both.
