#!/usr/bin/env bash
set -euo pipefail
kit="$1"
mkdir -p ~/.claude/agents
for agent_dir in "$kit"/agents/*/; do
    name="$(basename "$agent_dir")"
    dest=~/.claude/agents/"$name"
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$kit/agents/$name" ]; then
        echo "Already linked agent $name, no change"
    else
        ln -sfn "$kit/agents/$name" "$dest"
        echo "Linked agent $name into ~/.claude/agents"
    fi
done

# Prune links this kit made for agents that were renamed or removed - a
# plain "add/update" pass above never revisits a name that's gone.
for dest in ~/.claude/agents/*; do
    [ -L "$dest" ] || continue
    target="$(readlink "$dest")"
    case "$target" in
        "$kit"/agents/*)
            [ -d "$target" ] && continue
            rm "$dest"
            echo "Removed stale agent link $(basename "$dest") ($target no longer exists)"
            ;;
    esac
done
