# 070 - One launcher starts Claude as the bot, in a worktree

## Decision

The kit ships `scripts/kit-claude.sh`, aliased as `kit-claude` ([bot-account.md](../../conventions/bot-account.md), step 7). It starts `claude` as the bot account through `as-bot.sh`, and adds `--worktree` when run inside a git work tree. `kit-claude --self` starts Claude as the user instead; every other argument goes to `claude` unchanged.

The bot is the default and the user's own login is the opt-in. With no bot token, `kit-claude` stops with `as-bot`'s error and does not fall back to the user's login. There is no option to start without a worktree: the kit documents one way to start a session, and it is a worktree.

## Reason

Both habits, acting as the bot and working in a worktree, are meant to be the normal way to start a session, and typing them as `as-bot claude --worktree` each time invites skipping one. A `claude()` shell function that adds `--worktree` cannot do it: `as-bot.sh` ends in `exec "$@"`, which a script resolves through `PATH`, so it never sees the user's shell functions or aliases and would start a plain `claude`. A script in the kit works through `as-bot` and lives in the repo, where shellcheck covers it, not in each user's dotfiles.

The bot is the default because the bot is the limited credential: a session that forgot to opt in would act with the user's own, broader login. Failing without a token, instead of falling back, keeps a missing file from quietly widening what the session can do.

Alternatives rejected:

- **A `claude()` shell function in the user's dotfiles.** It does not reach `as-bot claude`, for the reason above, and its logic would be unreviewed and per user.
- **Teach `as-bot.sh` to add `--worktree`.** `as-bot` runs any command (`as-bot gh ...`), and would then know about one program's flags.
- **User login as the default, `--bot` to opt in.** The safer credential would then need remembering every time.
- **Fall back to the user's login without a token.** It turns a setup mistake into a session with more power than the user meant to give.
- **Pass a generated worktree name, `--worktree kit-<timestamp>`.** It would let `--worktree` stand before the arguments, but it gives up Claude Code's own names.

## Consequences

- `as-bot.sh` is unchanged and still runs any other command, by its path. The kit documents no alias for it.
- `--worktree` takes an optional name, so a flag placed before a prompt swallows it: `claude --worktree "fix the bug"` fails with an invalid worktree name, where `claude "fix the bug" --worktree` starts. The script therefore adds the flag after the user's arguments, and before a `--` if there is one.
- It leaves the flag off when the arguments already hold `-w` or `--worktree`, or resume a session with `-c`, `--continue`, `-r` or `--resume`. Claude Code returns a resumed session to the worktree it ended in, so adding the flag would only make a second one.
- The flag is left out outside a git work tree, which `claude` refuses with an error, and in a bare repo or a `.git` directory, where `git rev-parse --is-inside-work-tree` exits 0 but prints `false`.
- A session in a worktree finds `.fieldkit` through the `symlinkDirectories` entry that `just install` writes ([ADR 069](069-configure-new-worktrees.md)); without it the worktree has no link to the kit.
- `--self` counts only as the first argument. A later one goes to `claude`.
- The script resolves its own directory with `readlink -f` and stops if that fails. Without the check, a failed lookup would leave `as-bot.sh` to be looked up in the current directory, where a repo could plant one.
- If Claude Code gives `--worktree` a setting that makes it the default, drop the flag from the script and keep the rest.
