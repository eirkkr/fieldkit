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
