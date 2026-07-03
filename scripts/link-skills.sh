#!/usr/bin/env bash
set -euo pipefail
kit="$1"
mkdir -p ~/.claude/skills
for skill_dir in "$kit"/skills/*/; do
    name="$(basename "$skill_dir")"
    dest=~/.claude/skills/"$name"
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$kit/skills/$name" ]; then
        echo "Already linked /$name, no change"
    else
        ln -sfn "$kit/skills/$name" "$dest"
        echo "Linked /$name into ~/.claude/skills"
    fi
done
