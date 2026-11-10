#!/usr/bin/env bash
set -euo pipefail

# Start Claude as the bot account, in a git worktree when run inside a
# repo. The setup and what each part does are in
# conventions/bot-account.md (step 7).
#
#   kit-claude.sh [--self] [claude arguments]
#
# --self, as the first argument, starts Claude as you instead of the bot.
# Everything else goes to claude unchanged.

here="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

as_bot=true
if [ "${1:-}" = "--self" ]; then
    as_bot=false
    shift
fi

cmd=(claude)
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    cmd+=(--worktree)
fi
cmd+=("$@")

if [ "$as_bot" = true ]; then
    exec "$here/as-bot.sh" "${cmd[@]}"
fi
exec "${cmd[@]}"
