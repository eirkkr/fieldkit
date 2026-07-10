# Git conventions

- Never commit directly to the default branch. Branch, commit there, open a
  PR.

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
  (GitHub omits it when you provide a custom subject). Include `Closes #X`.
  Show the proposed message for approval before merging.
