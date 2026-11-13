#!/usr/bin/env bash
set -euo pipefail

# Make a worktree for new work beside the main checkout (ADR 073):
#
#     new-worktree.sh <type> <description>
#
# creates ../<repo>-<description> on branch <type>/<description>, cut from
# origin/<default-branch> with no upstream. Run it from anywhere in the repo,
# a linked worktree included. It prints the new worktree's absolute path on
# stdout and nothing else; every message goes to stderr.
#
# It refuses, creating nothing, when the branch name breaks conventions/git.md,
# the description is not lowercase letters, digits and hyphens, the path or the
# branch already exists, or the layout cannot work here: a parent directory
# that is not writable or sits inside another work tree, or a submodule.
#
# Exit codes: 1 refused or failed, 2 wrong usage.

kit="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

die() {
    echo "new-worktree: $*" >&2
    exit 1
}

usage() {
    echo "usage: new-worktree.sh <type> <description>" >&2
    exit 2
}

[ "$#" -eq 2 ] || usage
type="$1"
description="$2"

# The main checkout, found through the common git dir: from inside a linked
# worktree --show-toplevel would name that worktree, not the main one.
common="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" ||
    die "not inside a git repository"
case "$common" in
*/.git/modules/*) die "this repository is a submodule; the sibling layout does not apply to one" ;;
*/.git) main="${common%/.git}" ;;
*) die "no main checkout here (a bare repository?): the git dir is $common" ;;
esac
repo="$(basename "$main")"
parent="$(dirname "$main")"

[ -w "$parent" ] || die "$parent is not writable, so there is nowhere beside the repo to put a worktree"
if git -C "$parent" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    die "$parent is inside another git work tree; a worktree there would be tracked or scanned as part of it"
fi

# Name rules: the kit's own check covers the prefix and length (ADR 046), the
# description's characters are this script's.
[[ "$type" =~ ^[a-z]+$ ]] || die "type '$type' is not lowercase letters"
[[ "$description" =~ ^[a-z0-9-]+$ ]] || die "description '$description' is not lowercase letters, digits and hyphens"
branch="$type/$description"
if ! reason="$(python3 "$kit/hooks/conventions.py" branch "$branch" 2>&1)"; then
    die "$reason"
fi

path="$parent/$repo-$description"
if [ -e "$path" ] || git -C "$main" worktree list --porcelain | grep -qxF "worktree $path"; then
    die "$path already exists; it is not reused. Pick another description, or remove it first"
fi
if git -C "$main" show-ref --verify --quiet "refs/heads/$branch"; then
    die "branch $branch already exists"
fi

# Cut from the remote's default branch, refreshed first: origin/HEAD goes stale
# after a rename. Resolved in the order the pre-commit hook uses.
git -C "$main" fetch --quiet origin >&2 || die "could not fetch origin"
git -C "$main" remote set-head origin --auto >/dev/null 2>&1 || true
default="$(git -C "$main" config fieldkit.defaultBranch || true)"
if [ -z "$default" ]; then
    default="$(git -C "$main" symbolic-ref --quiet --short refs/remotes/origin/HEAD || true)"
    default="${default#origin/}"
fi
default="${default:-main}"
git -C "$main" rev-parse --verify --quiet "refs/remotes/origin/$default" >/dev/null ||
    die "origin/$default does not exist, so there is nothing to cut the branch from"

# --no-track: with a tracking branch, a plain `git push` could target the
# default branch.
if ! git -C "$main" worktree add --quiet --no-track -b "$branch" "$path" "origin/$default" >&2; then
    # A failed add can leave the branch behind, and a retry would be refused.
    git -C "$main" branch -D "$branch" >/dev/null 2>&1 || true
    die "git worktree add failed"
fi

echo "$path"
