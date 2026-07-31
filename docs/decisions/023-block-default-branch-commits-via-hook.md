# 023 - Block default-branch commits with a git hook

## Decision

The kit ships a `pre-commit` hook in a new `hooks/` area that refuses commits
when the checked-out branch is the repo's default branch. It's opt-in per repo
and per clone: `.fieldkit/scripts/enable-hooks.sh`, run from a consumer repo
root, symlinks `.git/hooks/pre-commit` to the kit's copy. `just install`
doesn't run it - that recipe wires machine-level state under `~/.claude` and
`~/.local/bin`, while `.git/hooks` lives inside each clone.

The hook takes the default branch from a `fieldkit.defaultBranch` git config
when set, otherwise `origin/HEAD`, otherwise `main`. It exits 0 on a detached
HEAD, so rebases and bisects are unaffected. `git commit --no-verify` remains
the escape hatch, and the hook's own message doesn't mention it.

## Reason

"Never commit directly to the default branch" has been rule one of
`conventions/git.md` since the start, but it's enforced only by instruction,
and instructions only work if something surfaces them at the moment of acting.
A Claude Code session in a consumer repo ran three `git commit`s straight onto
`main`, because it followed its own built-in commit procedure rather than
routing through the `push` skill that reads `git.md`.
[ADR 019](019-git-on-demand-via-skills.md) already moved partly in this
direction - `/push` branches off the default branch itself instead of merely
being told not to commit to main - but that only covers the path that goes
through the skill. A hook fires on the actual `git commit`, so it covers every
path: a human, a raw agent `Bash` call, or a subagent that skipped the skill.

This doesn't reopen [ADR 007](007-agents-dont-run-linters.md), which rejected
"a silent auto-fix hook". That rejection was about Claude Code settings hooks,
which don't travel through the `@.fieldkit` import, running repo-specific
format commands and feeding lint churn back to the agent. A git hook travels
through the symlink like everything else in the kit, is toolchain-independent,
and blocks rather than fixes - no output for an agent to iterate on.

Issue #41 (directing agents to prefer the `commit-push` skill over raw git)
stays worth doing and is unaffected. The two are complements: the directive
steers toward the delegation pattern, the hook backstops the worst outcome
when the directive isn't read.

Alternatives rejected:

- **`core.hooksPath` pointed at `.fieldkit/hooks`.** One git config setting
  rather than a script, and it would pick up future kit hooks automatically.
  Rejected because it replaces the hooks directory wholesale: any repo-local
  hook in `.git/hooks` silently stops firing, and the repo can never add one,
  since the shared kit owns that path. Per-hook symlinks compose instead.
- **Copying the hook into `.git/hooks`.** Simplest to install, but it's a
  snapshot - a kit fix never reaches repos that already ran the installer.
  That's exactly the copy-drift [ADR 001](001-import-not-copy.md) rejects.
- **Folding it into `just install`.** Would need `just install` to know every
  consumer repo's location, which it deliberately doesn't
  ([ADR 021](021-adopt-openspec-centralised-via-kit.md) drew the same
  machine-level/repo-level line for OpenSpec).
- **Advertising `--no-verify` in the refusal message.** Friendlier to a human
  who genuinely needs it, but an agent that reads "bypass with `--no-verify`"
  will bypass rather than branch, which is the exact failure this closes. The
  escape hatch is documented for humans in the README and `git.md` instead.

## Consequences

- `hooks/` becomes the kit's first git-hook area, the slot the README already
  reserved for growth. A second hook is an extra file plus a loop in
  `enable-hooks.sh`.
- Installation is per clone and easy to forget - a fresh checkout is
  unprotected until someone reruns the script. Accepted: `.git/` can't be
  version controlled, so any git-hook mechanism has this property.
- The kit installs the hook on itself, so `enable-hooks.sh` carries a small
  fallback for the repo that has no `.fieldkit` symlink pointing at it.
- Commands that commit on the default branch are now refused, including
  `git revert` and `git cherry-pick` onto it. Those belong on a branch under
  the same rule, so the refusal is correct rather than a false positive.
  Merge commits are unaffected - git runs `pre-merge-commit` for those.
- `origin/HEAD` is only a guess, and a clone may not have it set at all - this
  one didn't. The `fieldkit.defaultBranch` config takes precedence over it
  rather than merely filling in when it's missing, so a repo can always state
  the answer outright; the `main` fallback keeps the common case working with
  no configuration.
