# Reviews

The reviews to offer on this repo's plans and PRs, by what the work holds; when and how is `conventions/specs.md`, "Review". Offer the rows worth their cost for the work in hand.

| Skill or agent | When to offer |
| --- | --- |
| `mattpocock-skills:grilling` | Before a plan is written: the questions only the reviewer can answer |
| None - a fresh agent | A plan published: read as specs.md's "Review" describes |
| `mattpocock-skills:code-review` | Every PR. Standards: the diff against the convention docs and ADRs. Spec: against the issue or the stage's steps |
| `mattpocock-skills:writing-for-agents` | `KIT.md`, `CLAUDE.md`, a skill or a convention doc: what an agent reads, checked for restatement, no-ops and rules worth disclosing |
| `pr-review-toolkit:code-reviewer` | Logic in `scripts/` or `hooks/`: a diff that can go wrong in ways a check run misses, since the kit has no tests |
| `pr-review-toolkit:silent-failure-hunter` | A hook or check with a fallback or a swallowed exit: one that fails open passes everything |
| `pr-review-toolkit:comment-analyzer` | A script's or hook's comments, checked against the code beside them |
| `security-review` (built into Claude Code) | A workflow reading PR text, or a hook: hooks run on every tool call, on every machine with the kit installed |

- `code-reviewer` reads `CLAUDE.md` and unstaged changes by default. Give it the PR's diff (`git diff origin/main...HEAD`) and the convention docs the diff touches.
- `silent-failure-hunter` carries another stack's rules (Sentry, `logError`), which the kit has no counterpart for. Tell it to judge each failure path by what the hook or check is for: a check that exits 0 on an error reports a pass.
- `mattpocock-skills:code-review` runs its two axes in subagents that can invoke the skill again and fan out. Tell each to review directly and start no agents of its own.
