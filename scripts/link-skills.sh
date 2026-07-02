#!/usr/bin/env bash
set -euo pipefail
kit="$1"
mkdir -p ~/.claude/skills
dest=~/.claude/skills/kit-reconcile
if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$kit/skills/kit-reconcile" ]; then
    echo "Already linked /kit-reconcile, no change"
else
    ln -sfn "$kit/skills/kit-reconcile" "$dest"
    echo "Linked /kit-reconcile into ~/.claude/skills"
fi
