# Claude Guidance (this repo)

Field Kit's own repo-specific rules. The shared, cross-repo rules consumers import live in [KIT.md](KIT.md) and are imported at the foot of this file - edit those there, not here.

## This repo is public

The kit is a public repository ([ADR 036](docs/decisions/036-public-mit-with-upstream-notice.md)). Everything in it is world-readable, and so is everything *around* it: issues, pull request descriptions, comments, and commit messages are as public as the code.

- Never name a private repo here - not in docs, ADRs, commit messages, issue or PR text, or comments. Refer to one by role: "a consumer repo", "a Python consumer", "one consumer's ADR 010". This holds even when the private repo is the reason the change exists.
- Don't link to one either. A `github.com/<owner>/<private-repo>` URL or a `owner/repo#123` cross-reference names it just as plainly as prose does, and renders as a dead link for everyone who can't see it.
- Worked examples drawn from a private repo are welcome - the finding, the numbers, the file names, the failure. It's the repo's identity that stays out, not the substance.

## Paths differ from a consumer session

KIT.md's load-on-demand table gives targets as `.fieldkit/conventions/<file>`, which is correct in a consumer repo reaching the kit through its symlink. This repo has no `.fieldkit` symlink to itself ([ADR 014](docs/decisions/014-skills-not-commands.md)), so read those files at `conventions/<file>` instead.

## Reviews

The reviews to offer on a plan and on a PR, by what the work holds; when and how is `conventions/specs.md`, "Review". Offer the rows worth their cost for the work in hand.

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

## Shared rules

Everything below is [KIT.md](KIT.md), imported verbatim - the cross-repo rules every consumer gets. It carries its own heading.

@KIT.md
