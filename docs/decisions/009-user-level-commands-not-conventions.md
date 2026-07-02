# 009 - User-level for commands, per-repo opt-in for conventions

## Decision

Distribute the kit's two asset kinds differently:

- Slash commands (and later skills, agents) are version-controlled here under
  `commands/` and symlinked into `~/.claude/commands` by `just install`, making
  them available in every repo without per-repo wiring.
- Conventions stay per-repo opt-in via the `@.fieldkit/CLAUDE.md` import (see
  [ADR 006](006-symlink-kit-reference.md)). They are not loaded at user level.

We considered, and rejected, importing the conventions globally too - e.g.
`@~/src/fieldkit/CLAUDE.md` in `~/.claude/CLAUDE.md` - to drop the per-repo
symlink and import entirely.

## Reason

The two kinds differ in how they activate. A command is *pull*: inert until you
invoke it, so making it globally available costs nothing in a repo that never
calls it. A convention is *push*: it injects instructions into every turn of
every session in scope. Loading conventions at user level would apply them to
every directory Claude runs in - client repos, open-source contributions,
throwaway experiments - including ones where they are actively wrong (a repo
that wants `Co-Authored-By` trailers, American spelling, or different branch
rules), with no signal in that repo explaining the behaviour.

The per-repo `@.fieldkit` import is therefore a feature, not friction: it scopes
the conventions to repos that opt in, keeps the opt-in `python.md` selectable
per repo, and leaves an in-repo trace of why Claude behaves as it does. Global
loading would not even remove all setup - the load-on-demand convention files
are read during the session, so the kit clone still needs to be a readable
directory.

## Consequences

- Commands carry no per-repo setup; `just install` wires them once per machine
  (the symlink into `~/.claude` is not itself version-controlled).
- Conventions keep the per-repo symlink-and-import setup from ADR 006; this is
  accepted as the price of containment.
- The split generalises: future pull-style assets (skills, agents) go
  user-level; always-on instruction sets stay per-repo opt-in.
- If usage ever narrows to almost exclusively the owner's own repos, global
  conventions could be revisited - it trades containment for convenience and
  would supersede this decision.

Superseded by [ADR 014](014-skills-not-commands.md): the asset kind moved from
slash commands to Skills, but the user-level pull / per-repo push split this
ADR established is unchanged.
