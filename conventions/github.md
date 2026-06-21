# GitHub and external actions

- Show a draft and wait for approval before creating or editing issues or
  comments. Treat like destructive ops: confirm first.
- PRs are the exception: create and update them directly, no pre-approval of the
  title or body needed. The review gate is the pre-merge message (see
  [git.md](git.md)), not the PR itself.
- Before drafting an issue, check for duplicates/broader scope:
  `gh issue list --search "<2-3 keywords>"`.
- Create PRs with `--draft` unless explicitly told they're ready.
- Out-of-scope work -> file a narrow issue and defer; don't bundle it in.

## Issues

- Titles: imperative mood, no trailing period, ~72-character soft limit.
  Optionally prefix with the primary component when it adds clarity (e.g.
  `API:`, `Docs:`); the prefix list is per-repo and grows with the codebase.
- Use the bug template for anything broken, the feature template for new
  functionality. File refactors, chores, and docs without a template.
- Keep the description focused on the specific finding - a narrow,
  well-described issue is more actionable than a broad one.
