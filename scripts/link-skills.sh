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

# Prune links this kit made for skills that were renamed or removed - a
# plain "add/update" pass above never revisits a name that's gone.
for dest in ~/.claude/skills/*; do
    [ -L "$dest" ] || continue
    target="$(readlink "$dest")"
    case "$target" in
        "$kit"/skills/*)
            [ -d "$target" ] && continue
            rm "$dest"
            echo "Removed stale skill link $(basename "$dest") ($target no longer exists)"
            ;;
    esac
done
