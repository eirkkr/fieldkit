# 006 - Reach the kit through a per-consumer symlink

## Decision

Consumer repos reach this kit through a gitignored `.fieldkit` symlink at the
consumer repo root, pointing to wherever the kit is cloned. CLAUDE.md references
the kit by repo-relative paths through that symlink: the entry import is
`@.fieldkit/CLAUDE.md` and the load-on-demand table lists
`.fieldkit/conventions/<file>` targets. The kit no longer hardcodes its clone
location.

## Reason

[ADR 003](003-absolute-import-paths.md) hardcoded `~/src/fieldkit` throughout
CLAUDE.md so the load-on-demand Read targets - resolved in a consumer session -
would not miss. That pinned the kit to one clone path on every machine. A
fixed-name symlink in the consumer lets those paths be relative to the consumer,
so the shared kit stops naming its own location.

Symlink over git submodule: the kit is personal cross-repo dev guidance, not a
build dependency. A submodule pins a commit and vendors the content into each
consumer's tree, so every update means bumping and committing a pointer in every
consumer. A symlink keeps one clone as the single source of truth - a `git pull`
in the kit propagates everywhere at once. The submodule's benefits (version
pinning, surviving on machines/CI without the kit) do not apply here.

Gitignored over committed: a committed symlink bakes in an absolute target
(valid only where the kit sits at that path) or a relative one (valid only under
a fixed sibling layout). Gitignoring it and recreating per clone via a one-line
`ln -s` lets each machine point at its own kit location, at the cost of a setup
step per clone.

## Consequences

- Each consumer repo needs a one-time `.fieldkit` symlink and `.gitignore`
  entry; the README documents this, and it recurs on every clone, collaborator,
  and CI checkout.
- The load-on-demand targets are now relative, so they resolve only when the
  session's working directory is the consumer repo root. Consumers must start
  sessions there; the README documents this and CLAUDE.md notes the anchor by
  the table.
- The `@.fieldkit/CLAUDE.md` import resolves outside the consumer repo, so
  Claude Code prompts for external-import approval on first run; declining
  permanently disables it.
- The kit can be cloned anywhere; the location lives only in each consumer's
  symlink.
- Supersedes ADR 003.
