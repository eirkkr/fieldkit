#!/usr/bin/env bash
set -euo pipefail

# Start Claude as the bot account. The setup and what each part does are
# in conventions/bot-account.md (step 7).
#
#   kit-claude.sh [--self] [claude arguments]
#
# --self, as the first argument, starts Claude as you instead of the bot.
# Everything else goes to claude unchanged.

src="$(readlink -f "${BASH_SOURCE[0]}")" || src=""
here="$(dirname "$src")"
if [ -z "$src" ] || [ "${here#/}" = "$here" ]; then
    echo "kit-claude: cannot find the kit's scripts directory" >&2
    exit 1
fi

if [ "${1:-}" = "--self" ]; then
    shift
    exec claude "$@"
fi
exec "$here/as-bot.sh" claude "$@"
