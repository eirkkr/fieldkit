# Claude Guidance (this repo)

Field Kit's own repo-specific rules. The shared, cross-repo rules consumers
import live in [KIT.md](KIT.md) and are imported below - edit those there, not
here.

@KIT.md

## This repo is public

The kit is a public repository ([ADR 036](docs/decisions/036-public-mit-with-upstream-notice.md)).
Everything in it is world-readable, and so is everything *around* it: issues,
pull request descriptions, comments, and commit messages are as public as the
code.

- Never name a private repo here - not in docs, ADRs, commit messages, issue
  or PR text, or comments. Refer to one by role: "a consumer repo", "a Python
  consumer", "one consumer's ADR 010". This holds even when the private repo
  is the reason the change exists.
- Don't link to one either. A `github.com/<owner>/<private-repo>` URL or a
  `owner/repo#123` cross-reference names it just as plainly as prose does, and
  renders as a dead link for everyone who can't see it.
- Worked examples drawn from a private repo are welcome - the finding, the
  numbers, the file names, the failure. It's the repo's identity that stays
  out, not the substance.

## Paths differ from a consumer session

KIT.md's load-on-demand table gives targets as `.fieldkit/conventions/<file>`,
which is correct in a consumer repo reaching the kit through its symlink. This
repo has no `.fieldkit` symlink to itself ([ADR 014](docs/decisions/014-skills-not-commands.md)),
so read those files at `conventions/<file>` instead.
