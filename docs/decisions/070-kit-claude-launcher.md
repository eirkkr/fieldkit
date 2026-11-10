# 070 - One launcher starts Claude as the bot

## Decision

The kit ships `scripts/kit-claude.sh`, aliased as `kit-claude` ([bot-account.md](../../conventions/bot-account.md), step 7). It starts `claude` as the bot account through `as-bot.sh`. `kit-claude --self` starts Claude as the user instead; every other argument goes to `claude` unchanged.

The bot is the default and the user's own login is the opt-in. With no bot token, `kit-claude` stops with `as-bot.sh`'s error and does not fall back to the user's login.

## Reason

The bot is the limited credential, so a session that forgot to opt in would act with the user's own, broader login. Making the bot the default, and failing without a token instead of falling back, keeps a missing file from quietly widening what the session can do. A single name is also less to remember than `as-bot.sh claude`.

The launcher does not start Claude in a worktree. It did at first, through `claude --worktree`, and that was dropped for three reasons:

- **The branch name.** `claude --worktree` creates a branch named `worktree-<name>`, with a random name unless one is given. That breaks the prefix rule in [git.md](../../conventions/git.md), and neither the branch-name hook ([ADR 046](046-enforce-branch-names-in-a-hook-and-ci.md)) nor the launcher can rename it: the hook sees only Bash commands, and the launcher runs before any branch exists. Where the PR branch-name check is enabled, CI would reject the pull request, late.
- **The argument handling.** The flag takes an optional name, so it can only go after the user's arguments, and it must be left off for resume flags and `claude` subcommands. That took a scanner, a subcommand list copied from `claude --help`, and a workaround for bash before 4.4, for something the agent can do when it branches.
- **Where the rule belongs.** Working in a worktree is a rule about branching, so it lives with the branch rules in `git.md` and `KIT.md`: the agent enters a worktree with `EnterWorktree`, then renames the branch to a conforming name, which the hook checks.

Alternatives rejected:

- **A `claude()` shell function in the user's dotfiles.** Its logic would be unreviewed and per user, and a function named `claude` would also wrap the plain `claude` the user runs to opt out.
- **A `WorktreeCreate` hook that makes the worktree with a conforming branch.** Claude Code supports one, but it replaces Claude Code's own creation, so the kit would own the base branch, the `.fieldkit` link and the cleanup, and the hook gets only a `name`, not the agent's description of the work.
- **Teach `as-bot.sh` to know `claude`'s flags.** It runs any command (`as-bot.sh gh ...`).
- **User login as the default, `--bot` to opt in.** The safer credential would then need remembering every time.
- **Fall back to the user's login without a token.** It turns a setup mistake into a session with more power than the user meant to give.

## Consequences

- `as-bot.sh` is unchanged and still runs any other command, by its path. The kit documents no alias for it.
- `--self` counts only as the first argument. A later one goes to `claude`.
- The script resolves its own directory with `readlink -f` and stops if that fails. Without the check, a failed lookup would leave `as-bot.sh` to be looked up in the current directory, where a repo could plant one.
- The script expands no possibly-empty array, so it runs on the bash 3.2 that macOS ships.
