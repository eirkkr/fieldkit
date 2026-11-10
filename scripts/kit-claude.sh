#!/usr/bin/env bash
set -euo pipefail

# Start Claude as the bot account, in a git worktree when run inside a
# repo. The setup and what each part does are in
# conventions/bot-account.md (step 7).
#
#   kit-claude.sh [--self] [claude arguments]
#
# --self, as the first argument, starts Claude as you instead of the bot.
# Everything else goes to claude unchanged. --worktree is added after the
# arguments, never before: it takes an optional name, so a leading prompt
# would be read as one. It is left off when the arguments already carry
# -w/--worktree or resume a session (-c, -r), which returns to its own
# worktree.

src="$(readlink -f "${BASH_SOURCE[0]}")" || src=""
here="$(dirname "$src")"
if [ -z "$src" ] || [ "${here#/}" = "$here" ]; then
    echo "kit-claude: cannot find the kit's scripts directory" >&2
    exit 1
fi

as_bot=true
if [ "${1:-}" = "--self" ]; then
    as_bot=false
    shift
fi

add_worktree=false
if [ "$(git rev-parse --is-inside-work-tree 2>/dev/null)" = true ]; then
    add_worktree=true
fi

before=()
after=()
seen_dashes=false
for arg in "$@"; do
    if [ "$seen_dashes" = true ]; then
        after+=("$arg")
        continue
    fi
    case "$arg" in
        --)
            seen_dashes=true
            after+=("$arg")
            ;;
        -w | --worktree | --worktree=* | -c | --continue | -r | --resume | --resume=*)
            add_worktree=false
            before+=("$arg")
            ;;
        *) before+=("$arg") ;;
    esac
done

cmd=(claude "${before[@]}")
if [ "$add_worktree" = true ]; then
    cmd+=(--worktree)
fi
cmd+=("${after[@]}")

if [ "$as_bot" = true ]; then
    exec "$here/as-bot.sh" "${cmd[@]}"
fi
exec "${cmd[@]}"
