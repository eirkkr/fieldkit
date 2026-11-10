# 069 - Pin new worktrees to the remote default branch

## Decision

`just install` sets `worktree.baseRef` to `"fresh"` in `~/.claude/settings.json`, through `scripts/pin-worktree-base.sh`. A new Claude Code worktree then branches from `origin/<default-branch>`, never from the local `HEAD`.

The script writes silently when the file has no `worktree.baseRef` or already holds `"fresh"`. If the key holds another value, it shows the diff and asks before overwriting, as `disable-attribution.sh` does ([ADR 017](017-attribution-via-settings-not-instructions.md)).

## Reason

[git.md](../../conventions/git.md) says to branch off the default branch, because stacking work on a branch that can still change is an anti-pattern. That is an instruction. For worktrees there is a setting that guarantees the same outcome, and [ADR 013](013-style-rules-in-tooling-not-context.md) and ADR 017 prefer a deterministic mechanism over an instruction where one exists. The other value, `"head"`, branches from local `HEAD` including unpushed commits and feature-branch state, which is exactly the stacking `git.md` rules out.

`"fresh"` is Claude Code's default today, so the pin changes nothing now. It guards against a change of default and against a stray `"head"` set by hand, and it states the intent where a reader of `settings.json` can see it.

Alternatives rejected:

- **Rely on the default.** Correct today, but silent: nothing records the intent, and a default change would stack work with no warning.
- **Set it per repo in a committed `.claude/settings.json`.** The base branch is a machine-wide preference that every consumer repo shares, so per-repo wiring would repeat it in each one. This is the user-level versus per-repo split of [ADR 009](009-user-level-commands-not-conventions.md).
- **Drop the `git.md` instruction in favour of the setting.** The setting only controls where a new worktree starts. `git.md` governs every branch, including a plain `git checkout -b` in the main checkout and machines that never ran `just install`.

## Consequences

- The setting does not make worktrees the default: Claude Code has no setting for that, so starting in a worktree stays a `--worktree` flag, or a shell function that adds it.
- Keep the `git.md` branching bullet. This pin backs it for worktrees and does not replace it.
- `"head"` stays available for a one-off by editing `settings.json` by hand; the next `just install` asks before restoring `"fresh"`.
- If Claude Code renames or removes `worktree.baseRef`, update this ADR and `scripts/pin_worktree_base.py`.
