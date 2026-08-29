# Git conventions

- Never commit directly to the default branch. Branch, commit there, open a
  PR. The kit's `pre-commit` hook enforces this once installed (see Hooks).

## Branches

- [Conventional Branch](https://conventional-branch.github.io/) naming:
  `type/short-description`, lowercase, hyphen-separated.
- Allowed prefixes: `feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/`. No
  others (`refactor/`, `fix/`, `test/`, etc.).
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
  description`, lowercase, imperative mood, no trailing period. Aim for 50
  characters in the subject, hard limit 72.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- For more context, add a body after a blank line, wrapped at 72.
- Commit often - each coherent piece of work as it lands, not one batch at the
  end of a session. Small commits are easier to review, revert, and reword,
  and no approval is needed for any of them.

## Pull requests and merging

- PR title follows the same Conventional Commits format; no issue numbers in the
  title. When the work resolves a tracked issue, reference it with `Closes #X`
  in the body - and when it doesn't, there's simply no such line.
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

## Hooks

- The kit ships a `pre-commit` hook refusing commits on the default branch,
  backing the rule above structurally. Install it from the repo root with
  `.fieldkit/scripts/enable-hooks.sh` - once per clone, since `.git/hooks`
  isn't version controlled.
- It takes the default branch from the `fieldkit.defaultBranch` git config
  when set, otherwise `origin/HEAD`, otherwise `main`. Set that config to
  override the guess, or in a repo whose `origin/HEAD` isn't set.
- Don't reach for `--no-verify` to get past it - the refusal means the commit
  belongs on a branch. Create one and commit there.
