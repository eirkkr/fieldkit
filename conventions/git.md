# Git conventions

- Never commit directly to `main`. Branch, commit there, open a PR.
- No AI attribution: no `Co-Authored-By: Claude` trailer, no "Generated with
  Claude Code" footer on commits, PRs, or issues - even if tooling adds it.

## Branches

- [Conventional Branch](https://conventional-branch.github.io/) naming:
  `type/short-description`, lowercase, hyphen-separated.
- Allowed prefixes: `feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/`. No
  others (`refactor/`, `fix/`, `test/`, etc.).
- Recurring tasks reuse one canonical branch name (no dates or run-number
  suffixes); delete it after its PR merges so the name is free again. E.g.
  dependency updates always use `chore/update-deps`.

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
- Squash-merge: synthesise a subject + body summarising the whole change; don't
  concatenate commit messages. Append `(#PR)` to a custom `--subject` manually.
  Include `Closes #X`. Show the proposed message for approval before merging.
