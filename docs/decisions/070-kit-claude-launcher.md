# 070 - One launcher starts Claude as the bot, in a worktree

## Decision

The kit ships `scripts/kit-claude.sh`, aliased as `kit-claude` ([bot-account.md](../../conventions/bot-account.md), step 7). It starts `claude` as the bot account through `as-bot.sh`, and adds `--worktree` when run inside a git repo. `kit-claude --self` starts Claude as the user instead; every other argument goes to `claude` unchanged.

The bot is the default and the user's own login is the opt-in. With no bot token, `kit-claude` stops with `as-bot`'s error and does not fall back to the user's login.

## Reason

Both habits, acting as the bot and working in a worktree, are meant to be the normal way to start a session, and typing them as `as-bot claude --worktree` each time invites skipping one. A shell function that adds `--worktree` cannot do it: `as-bot.sh` ends in `exec "$@"`, which a script resolves through `PATH`, so it never sees the user's shell functions or aliases and would start a plain `claude`. A script in the kit works through `as-bot` and lives in the repo, where shellcheck covers it, not in each user's dotfiles.

The bot is the default because the bot is the limited credential: a session that forgot to opt in would act with the user's own, broader login. Failing without a token, instead of falling back, keeps a missing file from quietly widening what the session can do.

Alternatives rejected:

- **A `claude()` shell function in the user's dotfiles.** It does not reach `as-bot claude`, for the reason above, and its logic would be unreviewed and per user.
- **Teach `as-bot.sh` to add `--worktree`.** `as-bot` runs any command (`as-bot gh ...`), and would then know about one program's flags.
- **User login as the default, `--bot` to opt in.** The safer credential would then need remembering every time.
- **Fall back to the user's login without a token.** It turns a setup mistake into a session with more power than the user meant to give.

## Consequences

- `as-bot` stays as it is for other commands; `kit-claude` is only for Claude.
- Outside a git repo `--worktree` is left out, since Claude Code refuses it there.
- `--self` is read only as the first argument, so it never collides with a `claude` flag.
- A user who wants Claude in the current checkout, as the bot, runs `as-bot claude`.
- If Claude Code gives `--worktree` a setting that makes it the default, drop the flag from the script and keep the rest.
