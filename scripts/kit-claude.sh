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
# -w/--worktree, resume a session (-c, -r, --from-pr, --teleport), which
# returns to its own worktree, or start with one of claude's subcommands,
# which do not take it. The subcommand list is from `claude --help`; a new
# subcommand missing from it fails loudly ("unknown option '--worktree'").

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
case "${1:-}" in
    agents | attach | auth | auto-mode | doctor | gateway | import | install | logs | mcp | plugin | plugins | purge | respawn | rm | setup-token | stop | kill | ultrareview | update | upgrade)
        add_worktree=false
        ;;
esac

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
        -w* | --worktree | --worktree=* | -c* | --continue | -r* | --resume | --resume=* | --from-pr | --from-pr=* | --teleport | --teleport=*)
            add_worktree=false
            before+=("$arg")
            ;;
        *) before+=("$arg") ;;
    esac
done

# ${arr[@]+...} keeps an empty array from tripping `set -u` on bash before 4.4
# (macOS ships 3.2).
cmd=(claude ${before[@]+"${before[@]}"})
if [ "$add_worktree" = true ]; then
    cmd+=(--worktree)
fi
cmd+=(${after[@]+"${after[@]}"})

if [ "$as_bot" = true ]; then
    exec "$here/as-bot.sh" "${cmd[@]}"
fi
exec "${cmd[@]}"
