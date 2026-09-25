#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Check a branch name against conventions/git.md's Branches rules: the PR's
# branch in CI (GITHUB_HEAD_REF, set on pull_request runs - including the
# kit's reusable branch-name workflow, called from a consumer's), else the
# checked-out branch.
branch="${GITHUB_HEAD_REF:-$(git branch --show-current)}"

# Detached HEAD has no name to check, and the default branch is exempt - the
# rules name the branches work happens on, not the one it merges into.
# Resolved as the pre-commit hook does.
default="$(git config fieldkit.defaultBranch || true)"
if [ -z "$default" ]; then
    default="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD || true)"
    default="${default#origin/}"
fi
default="${default:-main}"
if [ -z "$branch" ]; then
    echo "Detached HEAD - no branch name to check"
    exit 0
fi
if [ "$branch" = "$default" ]; then
    echo "On the default branch '$default' - its name isn't checked"
    exit 0
fi

python3 "$kit/hooks/pretooluse-branch-name.py" --name "$branch"
echo "Branch name '$branch' follows the rules"
