#!/usr/bin/env bash
set -euo pipefail

# A profile's CDPATH makes `cd` print the directory it changes to, and a GIT_DIR
# git exports to a hook or `rebase --exec` points every git call at one repo.
# Neither may reach the lookups below, which all go by the current directory.
unset CDPATH GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE

# Make a worktree for new work beside the main checkout (ADR 073):
#
#     new-worktree.sh <type> <description>
#     new-worktree.sh --existing <branch>
#     new-worktree.sh --setup <path>
#
# The first creates ../<repo>-<description> on branch <type>/<description>,
# cut from origin/<default-branch> with no upstream. The second makes the
# sibling for a branch that already exists, locally or on origin only (resuming
# on another machine, or after its worktree was removed). Run either from
# anywhere in the repo, a linked worktree included. It prints the worktree's
# absolute path on stdout and nothing else; every message goes to stderr.
#
# Once the worktree exists it links .fieldkit into it, when the main checkout
# has one, and runs the repo's `just worktree-setup` recipe there, the recipe's
# output going to stderr. A repo with no justfile, or none with that recipe, is
# told so and the script exits 0; a justfile `just` cannot load is a failure.
# If the link or the recipe fails, or a git hook fails after the worktree is
# made, the worktree stays, the path is still printed, and the exit code is 3.
# The third form re-runs only the recipe in a worktree that exists; it prints
# nothing on stdout.
#
# It refuses, creating nothing, when the branch name breaks conventions/git.md,
# the description is not lowercase letters, digits and hyphens, the path
# exists, the branch exists (or, with --existing, does not), or the layout
# cannot work here: a parent directory that is not writable or sits inside
# another work tree, or a submodule.
#
# Exit codes: 1 refused or failed, 2 wrong usage, 3 worktree made but a git
# hook, its .fieldkit link or its setup recipe failed.

# Through readlink, not cd: a consumer runs this through its .fieldkit symlink.
kit="$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")")"
# This script as a pasteable command, for the messages that say what to run.
self="$(printf '%q' "$kit/scripts/new-worktree.sh")"

die() {
    echo "new-worktree: $*" >&2
    exit 1
}

usage() {
    echo "usage: new-worktree.sh <type> <description> | --existing <branch> | --setup <path>" >&2
    exit 2
}

existing=false
setup_path=""
case "${1:-}" in
    --existing)
        [ "$#" -eq 2 ] || usage
        existing=true
        branch="$2"
        # Split at the first slash, as a branch the script made would be.
        type="${branch%%/*}"
        description="${branch#*/}"
        [ "$type" != "$branch" ] || die "branch '$branch' has no type/ prefix"
        ;;
    --setup)
        [ "$#" -eq 2 ] || usage
        setup_path="$2"
        ;;
    *)
        [ "$#" -eq 2 ] || usage
        type="$1"
        description="$2"
        branch="$type/$description"
        ;;
esac

# The repo's setup recipe, run in the worktree $1 with its output on stderr.
# Returns 0 when it ran or the repo has none, 1 when it could not run or failed.
# A justfile `just` cannot load is a failure, not a missing recipe: an import of
# a gitignored file, or syntax newer than the installed `just`, looks the same
# as an absent recipe to `just --show`.
run_setup() {
    local dir="$1" name found="" summary
    for name in justfile Justfile .justfile; do
        if [ -f "$dir/$name" ]; then
            found="$name"
            break
        fi
    done
    if [ -z "$found" ]; then
        echo "new-worktree: $repo has no justfile, so no environment was built in $dir" >&2
        return 0
    fi
    if ! command -v just >/dev/null 2>&1; then
        echo "new-worktree: just is not installed, so the setup recipe was not run" >&2
        return 1
    fi
    if ! summary="$(cd "$dir" && just --summary 2>&1)"; then
        echo "new-worktree: just could not load $dir/$found: $summary" >&2
        echo "new-worktree: fix it, then: $self --setup $(printf '%q' "$dir")" >&2
        return 1
    fi
    if ! tr ' ' '\n' <<<"$summary" | grep -qx worktree-setup; then
        echo "new-worktree: $repo has no 'worktree-setup' recipe, so no environment was built in $dir" >&2
        return 0
    fi
    if ! (cd "$dir" && just worktree-setup >&2); then
        echo "new-worktree: 'just worktree-setup' failed in $dir; the worktree is kept" >&2
        echo "new-worktree: fix it, then: $self --setup $(printf '%q' "$dir")" >&2
        return 1
    fi
}

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

if [ -n "$setup_path" ]; then
    [ -d "$setup_path" ] || die "$setup_path is not a directory"
    setup_path="$(cd "$setup_path" && pwd -P)"
    other="$(git -C "$setup_path" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
    [ "$other" = "$common" ] || die "$setup_path is not a worktree of $repo"
    run_setup "$setup_path" || exit 3
    exit 0
fi

[ -w "$parent" ] || die "$parent is not writable, so there is nowhere beside the repo to put a worktree"
if git -C "$parent" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    die "$parent is inside another git work tree; a worktree there would be tracked or scanned as part of it"
fi

# Name rules: the kit's own check covers the prefix and length (ADR 046), the
# description's characters are this script's.
[[ "$type" =~ ^[a-z]+$ ]] || die "type '$type' is not lowercase letters"
[[ "$description" =~ ^[a-z0-9-]+$ ]] || die "description '$description' is not lowercase letters, digits and hyphens"
if ! reason="$(python3 "$kit/hooks/conventions.py" branch "$branch" 2>&1)"; then
    die "$reason"
fi

path="$parent/$repo-$description"
if [ -e "$path" ] || git -C "$main" worktree list --porcelain | grep -qxF "worktree $path"; then
    die "$path already exists; it is not reused. Pick another description, or remove it first. To re-run only its setup recipe: $self --setup $(printf '%q' "$path")"
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

local_branch=false
git -C "$main" show-ref --verify --quiet "refs/heads/$branch" && local_branch=true
remote_branch=false
git -C "$main" show-ref --verify --quiet "refs/remotes/origin/$branch" && remote_branch=true

# Run `git worktree add` with the arguments after $1, which says whether the add
# makes the branch. A hook that fails once the worktree is complete (git-lfs's
# post-checkout, say) makes git exit non-zero with the worktree and branch in
# place: keep them, carry on, and exit 3 at the end. Any other failure made no
# worktree: delete a branch the add made, or a retry would be refused.
hook_failed=false
add_worktree() {
    local makes_branch="$1"
    shift
    if git -C "$main" worktree add --quiet "$@" >&2; then
        return 0
    fi
    if git -C "$main" worktree list --porcelain | grep -qxF "worktree $path"; then
        echo "new-worktree: git reported a failure after making $path, probably a hook; the worktree is kept" >&2
        hook_failed=true
        return 0
    fi
    if $makes_branch; then
        git -C "$main" branch -D "$branch" >/dev/null 2>&1 || true
    fi
    die "git worktree add failed"
}

if $existing; then
    $local_branch || $remote_branch || die "branch $branch exists neither locally nor on origin"
    # With only the remote branch, git makes a local one tracking it.
    makes_branch=true
    if $local_branch; then makes_branch=false; fi
    add_worktree "$makes_branch" "$path" "$branch"
else
    $local_branch && die "branch $branch already exists; --existing makes a worktree for it"
    $remote_branch && die "branch $branch already exists on origin; --existing makes a worktree for it"
    # --no-track: with a tracking branch, a plain `git push` could target the
    # default branch.
    add_worktree true --no-track -b "$branch" "$path" "origin/$default"
fi

# The link first: the recipe may need .fieldkit. Every failure leaves the worktree.
status=0
if $hook_failed; then status=3; fi
linked=true
if [ -e "$main/.fieldkit" ] && [ ! -e "$path/.fieldkit" ]; then
    ln -s "$(readlink -f "$main/.fieldkit")" "$path/.fieldkit" || {
        echo "new-worktree: could not link .fieldkit into $path" >&2
        status=3
        linked=false
    }
fi
if $linked && ! run_setup "$path"; then status=3; fi

echo "$path"
exit "$status"
