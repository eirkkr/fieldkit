#!/usr/bin/env bash
set -euo pipefail

if [ -e ./.fieldkit/hooks/pre-commit ]; then
    target="../../.fieldkit/hooks/pre-commit"
elif [ -e ./hooks/pre-commit ]; then
    target="../../hooks/pre-commit"
else
    echo "./.fieldkit not found - see the kit README's consumer-repo setup" >&2
    exit 1
fi

if [ ! -d .git ]; then
    echo ".git/ not found - run this from the repo root (not a linked worktree)" >&2
    exit 1
fi

if [ -n "$(git config core.hooksPath || true)" ]; then
    echo "core.hooksPath is set - unset it, or install the hook there yourself" >&2
    exit 1
fi

dest=".git/hooks/pre-commit"
if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
    echo "Already linked .git/hooks/pre-commit, no change"
elif [ -f "$dest" ] && [ ! -L "$dest" ]; then
    echo "$dest already exists and isn't a symlink - move it aside first" >&2
    exit 1
else
    mkdir -p .git/hooks
    ln -sfn "$target" "$dest"
    echo "Linked .git/hooks/pre-commit"
fi

echo "Commits to the default branch are now refused. Rerun after a fresh clone - .git/hooks isn't version controlled."
