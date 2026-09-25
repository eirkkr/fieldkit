# Git conventions

- Never commit directly to the default branch. Branch, commit there, open a
  PR. The kit's `pre-commit` hook enforces this once installed (see Hooks
  and CI checks).

## Branches

- [Conventional Branch](https://conventional-branch.github.io/) naming:
  `type/short-description`, lowercase, hyphen-separated.
- Allowed prefixes: `feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/`. No
  others (`refactor/`, `fix/`, `test/`, etc.).
- At most 50 characters, prefix included - a few words of description. The
  issue or PR carries the detail.
- Branch off the default branch. Branching off another branch is an
  anti-pattern - it stacks work on something that can still change or get
  discarded.
- One branch is one unit of work, and for a review-gated OpenSpec change that
  unit is the *stage*, not the whole change: each stage gets its own branch
  off the default branch and merges when its review gate closes
  ([specs.md](specs.md)). A change spanning five stages is five branches in
  sequence, each cut from the previous one's merge - never stacked on a
  branch still under review.

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/): `type: short
  description`, imperative mood. No scope.
- A breaking change - one a consumer has to act on - is marked with `!`
  after the type (`feat!: drop the old flag`) and a `BREAKING CHANGE:` line
  in the body saying what to do. Each requires the other.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`. No others
  (`ci`, `style`, `perf`, `build`, etc.).
- The description starts lowercase and has no trailing period.
- The subject is at most 72 characters - GitHub cuts longer ones on its
  commit pages.
- For more context, add a body after a blank line, every line at most 72
  characters, so `git log`'s 4-space indent still fits 80 columns. A line
  that is one unbreakable word - a URL or a path, optionally after a list
  marker or a `[1]:` label - may run longer, since it can't be wrapped.
- Commit often - each coherent piece of work as it lands, not one batch at the
  end of a session. Small commits are easier to review, revert, and reword,
  and no approval is needed for any of them.

## Pull requests and merging

- PR title follows the Commits rules above. It becomes the squash subject once
  GitHub appends `(#N)`, so the 72 includes that suffix. A `!` title needs a
  `BREAKING CHANGE:` line in the PR body, which the squash body carries on.
  No issue numbers in the title. When the work resolves a tracked issue,
  reference it with `Closes #X` in the body - and when it doesn't, there's
  simply no such line.
- Always `git push` before `gh pr merge` (squash merge uses remote state).
- Work in progress stays on the branch - push freely, but don't open a PR
  until the work is ready for review. Draft the title and body yourself when
  opening it. Merge once CI is green and the PR has no conflicts - see
  Squash-merge below.
- Once a PR is open, every later push to that branch has to leave the
  description still true. Checking is part of the push, not a separate
  step: push first, check the body against the branch as pushed, and apply
  a revision right away if it's gone stale (see [github.md](github.md)).
- Squash-merge: synthesise a subject + body summarising the whole change; don't
  concatenate commit messages. Append `(#PR)` to a custom `--subject` manually
  (GitHub omits it when you provide a custom subject). Take `Closes #X` from
  `gh pr view --json closingIssuesReferences` - GitHub's own answer to what
  the PR closes - rather than reading a number off the body or inferring one.
  Nothing back means no linked issue: omit the line entirely. Never fall back
  to the PR's own number; issues and PRs share one number space, so a wrong
  guess still resolves to something. Merge once CI is green and the PR has
  no conflicts; a red check or unresolved conflicts block it outright, a
  still-running check is waited out instead.

## Rewriting history

- Rebasing or amending a pushed branch rewrites its commits, so the push
  after it is a force-push:
  `--force-with-lease=<branch>:<sha last seen>`, which refuses if anything
  landed since. Plain `--force`, and a bare `--force-with-lease` (which
  trusts whatever was last fetched), can overwrite someone else's push.
- The default branch is never rewritten.
- A rewrite re-SHAs every commit, so anything citing the old SHAs goes
  stale - a stage's review note especially (see [specs.md](specs.md)).

## Hooks and CI checks

- The kit ships two git hooks, installed from the repo root with
  `.fieldkit/scripts/enable-hooks.sh` - once per clone, since `.git/hooks`
  isn't version controlled:
  - `pre-commit` refuses commits on the default branch. It takes the default
    branch from the `fieldkit.defaultBranch` git config when set, otherwise
    `origin/HEAD`, otherwise `main`; set that config to override the guess,
    or in a repo whose `origin/HEAD` isn't set.
  - `commit-msg` refuses a commit breaking the Commits rules. Messages git
    writes itself - merges, reverts, `fixup!`, `squash!` - pass.
- Don't reach for `--no-verify` to get past either - a refusal means the
  commit belongs on a branch, or its message needs fixing.
- Two Claude Code `PreToolUse` hooks, registered by `just install`, act only
  in a repo with `.fieldkit` or in the kit, and only see Claude's Bash
  commands:
  - one refuses creating or renaming a branch to a name breaking the
    Branches rules, before anything is committed to it;
  - one checks the squash message Claude passes to `gh pr merge`: the
    Commits rules, plus the `(#N)` suffix matching the PR.
- CI checks each PR's title and its branch's name, however they were made -
  the title as the squash subject it becomes. Enable it from the repo root with
  `.fieldkit/scripts/enable-pr-checks.sh`, and commit the workflow it writes.
  PRs opened by bots are exempt, since bots name branches and PRs from their
  own config.
- All of these enforce the rules from constants in the kit's
  `hooks/conventions.py`, which mirror the Branches and Commits bullets
  above. A change to the rules changes both.
