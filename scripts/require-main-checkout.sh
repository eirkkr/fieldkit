#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Stop `just install` before it changes anything when it runs from a linked
# worktree of the kit. Install registers the kit's directory in
# ~/.claude/settings.json and in the skill, agent and statusline links, so a
# worktree's path would go dead when /merge removes the worktree, and the
# worktree-edit hook would stop guarding the main checkout.
git_dir="$(git -C "$kit" rev-parse --path-format=absolute --git-dir)"
common_dir="$(git -C "$kit" rev-parse --path-format=absolute --git-common-dir)"
if [ "$git_dir" != "$common_dir" ]; then
    # The first entry of `git worktree list` is the main worktree.
    main="$(git -C "$kit" worktree list --porcelain | sed -n '1s/^worktree //p')"
    echo "require-main-checkout: $kit is a linked worktree. Run 'just install' from the kit's main checkout: $main" >&2
    exit 1
fi
