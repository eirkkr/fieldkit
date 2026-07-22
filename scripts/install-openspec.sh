#!/usr/bin/env bash
set -euo pipefail
kit="$1"

min_version="20.19.0"
node_version="$(node --version | sed 's/^v//')"
if ! printf '%s\n%s\n' "$min_version" "$node_version" | sort -C -V; then
    echo "node >= $min_version required (found $node_version); run: sudo n lts" >&2
    exit 1
fi

npm ci --prefix "$kit"

dest=~/.local/bin/openspec
target="$kit/node_modules/.bin/openspec"
mkdir -p ~/.local/bin
if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
    echo "Already linked openspec, no change"
else
    ln -sfn "$target" "$dest"
    echo "Linked openspec into ~/.local/bin"
fi
