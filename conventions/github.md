# GitHub and external actions

- Show a draft and wait for approval before any externally-visible action
  (issues, PRs, comments). Treat like destructive ops: confirm first.
- Before drafting an issue, check for duplicates/broader scope:
  `gh issue list --search "<2-3 keywords>"`.
- Create PRs with `--draft` unless explicitly told they're ready.
- Out-of-scope work -> file a narrow issue and defer; don't bundle it in.
