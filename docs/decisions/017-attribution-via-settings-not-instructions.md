# 017 - Disable AI attribution via settings, not instructions

## Decision

`just install` sets `attribution: {commit: "", pr: "", sessionUrl: false}` in
`~/.claude/settings.json` (via `scripts/disable-attribution.sh`) instead of
relying on a conventions/git.md instruction telling the agent not to add
attribution. The old instruction bullet, and its cross-reference in
`agents/commit-push/AGENT.md`, have been removed.

Uses the `attribution` setting rather than the older `includeCoAuthoredBy`
boolean: Claude Code's docs mark `includeCoAuthoredBy` deprecated and note
`attribution` takes precedence over it.

## Reason

This follows the precedent of [ADR 013](013-style-rules-in-tooling-not-context.md):
an instruction is unreliable where a deterministic mechanism exists. The old
bullet even said "even if tooling adds it" - an admission that the instruction
alone couldn't guarantee compliance. Claude Code has a native setting for
exactly this behavior, so enforcing it there removes the cost from every
session's context and guarantees the outcome regardless of what the agent does.

Alternatives rejected:

- **Keep the instruction in conventions/git.md.** Costs context every session
  and isn't guaranteed - the very reason the bullet hedged with "even if
  tooling adds it."
- **Set `attribution` per-repo in a committed `.claude/settings.json`.**
  Attribution preference is a personal, machine-wide choice, not a per-project
  one, and would need wiring in every consumer repo. Matches the user-level vs
  per-repo split from [ADR 009](009-user-level-commands-not-conventions.md):
  this is a user preference, not a project convention.
- **Patch settings.json silently, like `register-dir.sh` does for
  `additionalDirectories` and `autoMemoryEnabled`.** Those are additive or
  low-stakes. Attribution is a behavioral preference a user may have
  deliberately set otherwise, so `disable-attribution.sh` shows a diff and
  asks before overwriting a differing existing value; it only writes silently
  when there's nothing to conflict with (file absent, or already disabled).

## Consequences

- `just install` is the source of truth for this behavior instead of docs; a
  fresh machine gets it automatically, an existing machine is prompted only if
  its settings already disagree.
- Consumers no longer need to read a convention to get this behavior - it
  applies globally after `just install`, independent of which repo a session
  runs in.
- If Claude Code ever changes or removes the `attribution` setting, this ADR
  and `scripts/disable_attribution.py` are what to update, not
  conventions/git.md.
