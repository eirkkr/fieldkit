# 014 - Skills, not slash commands, for shared pull-style assets

## Decision

Replace `commands/` with `skills/`: the kit's shared, pull-style Claude Code
assets are now distributed as Skills, not legacy slash-command files. `just
install` symlinks each skill's directory (e.g. `skills/kit-reconcile/`) into
`~/.claude/skills/`, making it available in every repo without per-repo wiring
- the same reach ADR 009 established for commands.

The source stays at a plain top-level `skills/`, not `.claude/skills/`.
Claude Code auto-discovers `.claude/skills/` as *this repo's own* project
skills; putting the shared source there would make `/kit-reconcile` available
inside the kit repo itself, where it makes no sense - this repo doesn't
`@`-import `.fieldkit/CLAUDE.md` from itself and has no `.fieldkit-rev`
marker to reconcile. `commands/` avoided this the same way: it was never
`.claude/commands/`, so the shipped source stayed inert until symlinked
user-level.

This supersedes the mechanism in [ADR 009](009-user-level-commands-not-conventions.md);
its push/pull placement reasoning (pull-style assets go user-level, always-on
conventions stay per-repo opt-in) is unchanged and still applies.

## Reason

Skills are the superset: a Skill still supports manual `/name` invocation with
the same frontmatter (`argument-hint`, `disable-model-invocation`,
`allowed-tools`) a slash command had, but also lets Claude invoke it by
description-matching intent when that's wanted, and lets a skill bundle more
than one file (scripts, references) under its directory instead of being
capped at a single markdown file. Keeping both mechanisms side by side would
mean two symlinking scripts and two mental models for what is otherwise one
kind of asset; folding commands into skills removes that split.

Alternatives rejected:

- **Keep `commands/` and add `skills/` alongside it.** ADR 009 anticipated this
  ("later skills, agents"), but running both mechanisms for the same purpose
  (pull-style, user-level assets) is pure overhead once skills cover
  everything commands did.

## Consequences

- `commands/kit-reconcile.md` is gone; `skills/kit-reconcile/SKILL.md` is the
  canonical source, editable in place.
- `scripts/link-commands.sh` is replaced by `scripts/link-skills.sh`, which
  symlinks a directory (`~/.claude/skills/kit-reconcile`) rather than a single
  file.
- Future pull-style assets (further skills, agents) follow this same path:
  version-controlled here under `skills/`, symlinked user-level by
  `just install`.
