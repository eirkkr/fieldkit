# 037 - Split the kit's shared entry point from its own rules

## Decision

The shared entry point consumers `@`-import is `KIT.md`. The root `CLAUDE.md`
is now the kit's *own* repo-specific guidance, which imports `KIT.md` so a
session in this repo gets both.

The first repo-specific rule it carries: this repository is public, so no
private repo may be named or linked in its docs, ADRs, commit messages, issues,
PRs, or comments. The generic form of that rule - a public repo doesn't name a
private one - lives in `conventions/github.md`, where every consumer gets it.

## Reason

The root `CLAUDE.md` was doing two jobs: the shared file consumers import, and
this repo's own project memory, since Claude Code loads `./CLAUDE.md`
automatically. That left the kit with nowhere to put a rule that applies to
itself. Its own first bullet already said repo-specific conventions belong in
the consumer repo's own docs - the kit just had no such place for its own.

The need became concrete when the repo was prepared for publication
([ADR 036](036-public-mit-with-upstream-notice.md)). A sweep found two private
project names in 22 places - 6 issues, 9 PRs, an issue comment, and 6 commits -
every one written by an agent with no rule telling it not to. Genericising the
text fixes what exists; only a rule prevents the next one.

Alternatives rejected:

- **Put the rule in the shared file.** It would ship to every consumer, where
  it is either wrong or noise, and it contradicts that file's own contract.
- **`CLAUDE.local.md`.** Auto-loaded and needs no import change, but it is
  gitignored: absent on a fresh clone, invisible to collaborators and CI. A
  rule that must hold for every agent cannot live somewhere that vanishes.
- **The generic `github.md` rule alone.** It protects any public consumer, and
  it is worth having on its own - but nothing would tell an agent that *this*
  repo is public, so the rule would not reliably fire where it matters most.
  Kept, as the generic half of a two-part fix.

`KIT.md` over a nested path like `shared/CLAUDE.md`: flat and content-shaped,
per [ADR 005](005-flat-repo-structure.md).

## Consequences

- **Breaking for existing consumers.** `@.fieldkit/CLAUDE.md` no longer
  resolves; each consumer's import line becomes `@.fieldkit/KIT.md`. Until it
  is changed, that session runs without the kit's always-on rules, which is not
  obvious from inside it - `/memory` is the check. The README carries the
  migration note.
- A consumer importing the old path would otherwise have picked up rules
  written for the kit - the split prevents that, which is the point.
- The kit's root `CLAUDE.md` also records that this repo has no `.fieldkit`
  symlink to itself ([ADR 014](014-skills-not-commands.md)), so `KIT.md`'s
  `.fieldkit/conventions/<file>` targets are read here at `conventions/<file>`.
  That mismatch predates this ADR and was previously unwritten.
- Future repo-specific rules for the kit now have an obvious home, rather than
  pressure to generalise them into the shared file.
- Import placement now matters and is documented. `KIT.md` keeps its own H1,
  since it is also read standalone as the kit's manual, and imports expand in
  place - so an import above a repo's own rules leaves them reading as
  subsections of the generic guidance. Both the kit's `CLAUDE.md` and the
  README's setup step put the import at the foot.
