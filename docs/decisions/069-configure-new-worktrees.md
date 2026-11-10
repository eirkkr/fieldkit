# 069 - Configure new worktrees: the remote default base and the .fieldkit link

## Decision

`just install` sets two keys under `worktree` in `~/.claude/settings.json`, through `scripts/configure-worktree.sh`:

- `baseRef` to `"fresh"`, so a new Claude Code worktree branches from `origin/<default-branch>`, never from the local `HEAD`.
- `symlinkDirectories` to include `".fieldkit"`, so a new worktree gets the `.fieldkit` link a consumer repo keeps in its main checkout.

The script first writes whatever replaces nothing, without asking: a missing or null `worktree`, `baseRef` or `symlinkDirectories` is filled, and `.fieldkit` is appended to a list that lacks it. Then it shows the diff and asks before replacing anything the user holds: a different `baseRef`, a `symlinkDirectories` that is not a list, or a `worktree` that is not an object. Declining a `baseRef` question therefore keeps the `.fieldkit` link and leaves the held value alone. Where the shape itself is wrong (a `worktree` or `symlinkDirectories` of the wrong type), nothing is written until the user accepts. This is narrower than `disable-attribution.sh` ([ADR 017](017-attribution-via-settings-not-instructions.md)), which asks whenever an existing file differs. When both keys are already right it changes nothing.

## Reason

**The base branch.** [git.md](../../conventions/git.md) says to branch off the default branch, because stacking work on a branch that can still change is an anti-pattern. That is an instruction. For worktrees there is a setting that guarantees the same outcome, and [ADR 013](013-style-rules-in-tooling-not-context.md) and ADR 017 prefer a deterministic mechanism over an instruction where one exists. The other value, `"head"`, branches from local `HEAD` including unpushed commits and feature-branch state, which is exactly the stacking `git.md` rules out. `"fresh"` is Claude Code's default today, so this half changes nothing now. It guards against a change of default and a stray `"head"`, and it states the intent where a reader of `settings.json` can see it.

**The `.fieldkit` link.** A worktree holds only tracked files, and a consumer repo gitignores its `.fieldkit` link ([ADR 006](006-symlink-kit-reference.md)), so a session started in a new worktree has no `.fieldkit`. Its `@.fieldkit/KIT.md` import and the `.fieldkit/conventions/<file>` paths in `KIT.md` then resolve to nothing. `symlinkDirectories` links the main checkout's `.fieldkit` into each new worktree. Checked against Claude Code 2.1.322: a worktree made with the entry has `.fieldkit` linked to the main checkout's, which resolves to the kit; one made without it has none; an entry whose source does not exist is skipped without an error; and a repo that tracks `.fieldkit` as a real directory keeps it, unreplaced. So a machine-wide entry costs a repo that does not use the kit nothing.

Alternatives rejected:

- **Rely on the defaults.** The base is right today but silent, and the link is missing, so a session in a worktree would lose the kit's rules.
- **Set them per repo in a committed `.claude/settings.json`.** Both are machine-wide preferences, not project ones, so per-repo wiring would repeat them in every consumer repo and miss a repo that is not one. Like attribution in ADR 017, they belong in user settings.
- **Drop the `git.md` instruction in favour of the base setting.** The setting only controls where a new worktree starts. `git.md` governs every branch, including a plain `git checkout -b` in the main checkout and machines that never ran `just install`.
- **Two scripts, one per key.** They edit the same object in the same file, so one script keeps a single read and write and a single prompt.

## Consequences

- The settings do not make worktrees the default: Claude Code has no setting for that, so starting in a worktree stays a `--worktree` flag, which `kit-claude` adds ([ADR 070](070-kit-claude-launcher.md)).
- Keep the `git.md` branching bullet. The base setting backs it for worktrees and does not replace it.
- Entries a user already has in `symlinkDirectories` stay; `.fieldkit` is appended.
- `"head"` stays available for a one-off by editing `settings.json` by hand; the next `just install` asks before restoring `"fresh"`, and keeps the `.fieldkit` link whichever way you answer.
- If Claude Code renames or removes either key, update this ADR and `scripts/configure_worktree.py`.
