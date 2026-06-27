#!/usr/bin/env bash
set -euo pipefail
kit="$1"
mkdir -p ~/.claude/commands
dest=~/.claude/commands/kit-reconcile.md
if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$kit/commands/kit-reconcile.md" ]; then
    echo "Already linked /kit-reconcile, no change"
else
    ln -sf "$kit/commands/kit-reconcile.md" "$dest"
    echo "Linked /kit-reconcile into ~/.claude/commands"
fi
