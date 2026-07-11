#!/usr/bin/env bash
set -euo pipefail
kit="$1"
dest=~/.claude/statusline-command.sh
if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$kit/statusline/statusline-command.sh" ]; then
    echo "Already linked statusline-command.sh, no change"
else
    ln -sfn "$kit/statusline/statusline-command.sh" "$dest"
    echo "Linked statusline-command.sh into ~/.claude"
fi
