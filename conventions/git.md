# Git conventions

- Never commit directly to the default branch. Branch, commit there, open a
  PR. The kit's `pre-commit` hook enforces this once installed (see Hooks).

## Branches

- [Conventional Branch](https://conventional-branch.github.io/) naming:
  `type/short-description`, lowercase, hyphen-separated.
- Allowed prefixes: `feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/`. No
  others (`refactor/`, `fix/`, `test/`, etc.).

## Commits

- [Conventional Commits](https://www.conventionalcommits.org/): `type: short
  description`, lowercase, imperative mood, no trailing period. Aim for 50
  characters in the subject, hard limit 72.
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
- For more context, add a body after a blank line, wrapped at 72.

## Pull requests and merging

- PR title follows the same Conventional Commits format; no issue numbers in the
  title. Reference the issue with `Closes #X` in the body.
- Always `git push` before `gh pr merge` (squash merge uses remote state).
- Work in progress stays on the branch - push freely (act-then-show), but don't
  open a PR until the work is ready for review. When it is, surface a compare
  link (`.../compare/<base>...branch`) and a short summary, and get approval before
  opening the PR - opening it asserts readiness. The pre-merge message is the
  merge gate.
- Squash-merge: synthesise a subject + body summarising the whole change; don't
  concatenate commit messages. Append `(#PR)` to a custom `--subject` manually
  (GitHub omits it when you provide a custom subject). Only add `Closes #X`
  when the PR actually resolves a tracked issue - `X` is that issue's number,
  never the PR's own. Omit the line entirely when there's no linked issue;
  don't invent one. Show the proposed message for approval before merging.

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
