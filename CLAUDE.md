# Claude Guidance (this repo)

Field Kit's own repo-specific rules. Shared cross-repo rules consumers import live in [KIT.md](KIT.md), imported at this file's foot: edit them there, not here.

## This repo is public

The kit is a public repository ([ADR 036](docs/decisions/036-public-mit-with-upstream-notice.md)). Everything in it is world-readable, and so is everything *around* it: issues, PR descriptions, comments and commit messages are as public as the code.

- Never name a private repo here: not in docs, ADRs, commit messages, issue or PR text, or comments. Refer to one by role: "a consumer repo", "a Python consumer", "one consumer's ADR 010". This holds even when the private repo is the reason the change exists.
- Never link to one either. A `github.com/<owner>/<private-repo>` URL or an `owner/repo#123` cross-reference names it as plainly as prose, and renders as a dead link for everyone who can't see it.
- Worked examples drawn from a private repo are welcome: the finding, numbers, file names, failure. The repo's identity stays out, not the substance.

## Paths differ from a consumer session

KIT.md's load-on-demand table gives targets as `.fieldkit/conventions/<file>`, correct in a consumer repo reaching the kit through its symlink. This repo has no `.fieldkit` symlink to itself ([ADR 014](docs/decisions/014-skills-not-commands.md)): read those files at `conventions/<file>`.

## Reviews

Before offering reviews on a plan or a PR, read [docs/reviews.md](docs/reviews.md).

## Shared rules

Everything below is [KIT.md](KIT.md), imported verbatim: the cross-repo rules every consumer gets. It carries its own heading.

@KIT.md
