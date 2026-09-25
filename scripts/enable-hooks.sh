#!/usr/bin/env bash
set -euo pipefail

if [ -e ./.fieldkit/hooks/pre-commit ]; then
    hooks="../../.fieldkit/hooks"
elif [ -e ./hooks/pre-commit ]; then
    hooks="../../hooks"
else
    echo "./.fieldkit not found - see the kit README's consumer-repo setup" >&2
    exit 1
fi

if [ ! -d .git ]; then
    echo ".git/ not found - run this from the repo root (not a linked worktree)" >&2
    exit 1
fi

if [ -n "$(git config core.hooksPath || true)" ]; then
    echo "core.hooksPath is set - unset it, or install the hooks there yourself" >&2
    exit 1
fi

mkdir -p .git/hooks
status=0
for hook in pre-commit commit-msg; do
    target="$hooks/$hook"
    dest=".git/hooks/$hook"
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
        echo "Already linked .git/hooks/$hook, no change"
    elif [ -f "$dest" ] && [ ! -L "$dest" ]; then
        echo "$dest already exists and isn't a symlink - move it aside first" >&2
        status=1
    else
        ln -sfn "$target" "$dest"
        echo "Linked .git/hooks/$hook"
    fi
done

if [ "$status" -eq 0 ]; then
    echo "Commits to the default branch, and commit messages breaking the rules, are now refused. Rerun after a fresh clone - .git/hooks isn't version controlled."
fi
exit "$status"
