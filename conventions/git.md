# Git conventions

- Never commit directly to `main`. Branch, commit there, open a PR.
- No AI attribution: no `Co-Authored-By: Claude` trailer, no "Generated with
  Claude Code" footer on commits, PRs, or issues - even if tooling adds it.
- Always `git push` before `gh pr merge` (squash merge uses remote state).
- Allowed branch prefixes: `feature/`, `bugfix/`, `hotfix/`, `release/`,
  `chore/`. No others (`refactor/`, `fix/`, `test/`, etc.).
- Squash-merge: synthesise a subject + body summarising the whole change; don't
  concatenate commit messages. Append `(#PR)` to a custom `--subject` manually.
  Include `Closes #X`. Show the proposed message for approval before merging.
