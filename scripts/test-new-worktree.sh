#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Test scripts/new-worktree.sh against throwaway repos: a bare remote, a clone
# of it, and the sibling worktrees the script makes beside the clone. Prints a
# line per case, prefixed with the recipe name, and exits 1 if any failed.

script="$kit/scripts/new-worktree.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir "$tmp/remotes" "$tmp/work"

# Nothing from the machine's git config may reach the throwaway repos.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
failed=0

# mkrepo <name> [<justfile body>]: a clone at $tmp/work/<name> with one commit
# on main, pushed to a bare remote, with the justfile committed when given.
mkrepo() {
    local name="$1" dir="$tmp/work/$1"
    git init -q --bare -b main "$tmp/remotes/$name.git"
    git clone -q "$tmp/remotes/$name.git" "$dir" 2>/dev/null
    if [ -n "${2:-}" ]; then
        printf '%s' "$2" >"$dir/justfile"
        git -C "$dir" add justfile
    fi
    git -C "$dir" commit -q --allow-empty -m init
    git -C "$dir" push -q origin main
    git -C "$dir" remote set-head origin main
}

# run <dir> <args...>: run the script from <dir>, setting $out, $err and $rc.
run() {
    local dir="$1"
    shift
    rc=0
    out="$(cd "$dir" && "$script" "$@" 2>"$tmp/err")" || rc=$?
    err="$(cat "$tmp/err")"
}

# snapshot <repo dir>: the branches, and the directories beside the repo.
snapshot() {
    git -C "$1" branch --list --all
    ls "$(dirname "$1")"
}

# refused <name> <dir> <fragment> <args...>: the script exits 1 naming
# <fragment> and leaves no new branch or directory behind.
refused() {
    local name="$1" dir="$2" fragment="$3" before
    shift 3
    before="$(snapshot "$dir")"
    run "$dir" "$@"
    [ "$rc" -eq 1 ] || { echo "exit $rc, not 1" >&2; return 1; }
    [[ "$err" == *"$fragment"* ]] || { echo "stderr lacks '$fragment': $err" >&2; return 1; }
    [ -z "$out" ] || { echo "stdout is not empty: $out" >&2; return 1; }
    [ "$(snapshot "$dir")" = "$before" ] || { echo "$name left something behind" >&2; return 1; }
}

case_creates_beside_the_repo() {
    mkrepo api
    run "$tmp/work/api" chore try-it
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [ "$out" = "$tmp/work/api-try-it" ] || { echo "stdout is '$out'" >&2; return 1; }
    [ "$(git -C "$out" branch --show-current)" = chore/try-it ] || return 1
    [ "$(git -C "$out" rev-parse HEAD)" = "$(git -C "$tmp/work/api" rev-parse origin/main)" ] || return 1
    ! git -C "$out" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1 || { echo "branch has an upstream" >&2; return 1; }
}

case_creates_from_inside_a_worktree() {
    mkrepo inner
    run "$tmp/work/inner" chore first
    run "$out" bugfix second
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [ "$out" = "$tmp/work/inner-second" ] || { echo "stdout is '$out'" >&2; return 1; }
}

case_refuses_a_bad_prefix() {
    mkrepo prefix
    refused prefix "$tmp/work/prefix" "no allowed prefix" nope thing
}

case_refuses_a_long_name() {
    mkrepo long
    refused long "$tmp/work/long" "over the 50-character limit" chore "$(printf 'a%.0s' {1..50})"
}

case_refuses_an_uppercase_description() {
    mkrepo upper
    refused upper "$tmp/work/upper" "lowercase letters, digits and hyphens" chore Upper
}

case_refuses_an_underscore_description() {
    mkrepo under
    refused under "$tmp/work/under" "lowercase letters, digits and hyphens" chore a_b
}

case_refuses_an_existing_path() {
    mkrepo taken
    mkdir "$tmp/work/taken-x"
    refused taken "$tmp/work/taken" "already exists" chore x
}

case_refuses_an_existing_branch() {
    mkrepo local
    git -C "$tmp/work/local" branch chore/x
    refused local "$tmp/work/local" "branch chore/x already exists" chore x
}

case_refuses_a_branch_on_origin() {
    mkrepo remote
    git -C "$tmp/work/remote" push -q origin main:chore/x
    refused remote "$tmp/work/remote" "already exists on origin" chore x
}

case_refuses_a_parent_inside_a_work_tree() {
    mkdir "$tmp/outer"
    git -C "$tmp/outer" init -q
    git init -q --bare -b main "$tmp/remotes/nested.git"
    git clone -q "$tmp/remotes/nested.git" "$tmp/outer/nested" 2>/dev/null
    git -C "$tmp/outer/nested" commit -q --allow-empty -m init
    git -C "$tmp/outer/nested" push -q origin main
    refused nested "$tmp/outer/nested" "inside another git work tree" chore x
}

case_refuses_a_submodule() {
    mkrepo sub
    mkrepo super
    git -C "$tmp/work/super" -c protocol.file.allow=always submodule -q add "$tmp/remotes/sub.git" lib 2>/dev/null
    refused submodule "$tmp/work/super/lib" "submodule" chore x
}

case_refuses_an_unwritable_parent() {
    [ "$(id -u)" -ne 0 ] || return 0 # root writes anywhere
    mkdir "$tmp/locked"
    git init -q --bare -b main "$tmp/remotes/locked.git"
    git clone -q "$tmp/remotes/locked.git" "$tmp/locked/repo" 2>/dev/null
    git -C "$tmp/locked/repo" commit -q --allow-empty -m init
    git -C "$tmp/locked/repo" push -q origin main
    chmod a-w "$tmp/locked"
    local rc_=0
    refused locked "$tmp/locked/repo" "not writable" chore x || rc_=$?
    chmod u+w "$tmp/locked"
    return "$rc_"
}

# A failed `git worktree add` can leave the branch it made. A stand-in git
# makes the add fail after creating the branch, as an unwritable parent would.
case_deletes_a_branch_a_failed_add_made() {
    mkrepo stray
    local real
    real="$(command -v git)"
    mkdir "$tmp/bin"
    cat >"$tmp/bin/git" <<EOF
#!/usr/bin/env bash
for arg in "\$@"; do
    if [ "\$arg" = add ] && [[ " \$* " == *" worktree "* ]]; then
        while [ "\$#" -gt 0 ]; do
            if [ "\$1" = -b ]; then "$real" -C "$tmp/work/stray" branch "\$2" origin/main; fi
            shift
        done
        echo "fatal: simulated failure" >&2
        exit 128
    fi
done
exec "$real" "\$@"
EOF
    chmod +x "$tmp/bin/git"
    local path_before="$PATH" rc_=0
    export PATH="$tmp/bin:$PATH"
    run "$tmp/work/stray" chore x
    export PATH="$path_before"
    [ "$rc" -eq 1 ] || { echo "exit $rc, not 1" >&2; return 1; }
    ! git -C "$tmp/work/stray" show-ref --verify --quiet refs/heads/chore/x || { echo "stray branch left" >&2; return 1; }
    run "$tmp/work/stray" chore x
    [ "$rc" -eq 0 ] || { echo "retry exit $rc: $err" >&2; return 1; }
}

case_existing_after_removal() {
    mkrepo again
    run "$tmp/work/again" chore one
    git -C "$tmp/work/again" worktree remove "$out"
    run "$tmp/work/again" --existing chore/one
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [ "$out" = "$tmp/work/again-one" ] || { echo "stdout is '$out'" >&2; return 1; }
    [ "$(git -C "$out" branch --show-current)" = chore/one ] || return 1
}

case_existing_from_origin_only() {
    mkrepo elsewhere
    git -C "$tmp/work/elsewhere" push -q origin main:chore/other
    run "$tmp/work/elsewhere" --existing chore/other
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [ "$(git -C "$out" branch --show-current)" = chore/other ] || return 1
}

case_existing_refuses_a_missing_branch() {
    mkrepo missing
    refused missing "$tmp/work/missing" "neither locally nor on origin" --existing chore/nope
}

case_runs_the_setup_recipe() {
    mkrepo built $'worktree-setup:\n\techo built > built.txt\n'
    run "$tmp/work/built" chore x
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [ "$(cat "$out/built.txt")" = built ] || return 1
}

case_keeps_a_worktree_whose_recipe_fails() {
    mkrepo broken $'worktree-setup:\n\texit 7\n'
    run "$tmp/work/broken" chore x
    [ "$rc" -eq 3 ] || { echo "exit $rc, not 3" >&2; return 1; }
    [ "$out" = "$tmp/work/broken-x" ] || { echo "stdout is '$out'" >&2; return 1; }
    [ -d "$out" ] || return 1
    # The recipe's own output is on stderr, never stdout.
    [[ "$err" == *"--setup $out"* ]] || { echo "no pointer to --setup: $err" >&2; return 1; }
}

case_setup_reruns_the_recipe() {
    mkrepo retry $'worktree-setup:\n\t[ -e ok ] && echo built > built.txt\n'
    run "$tmp/work/retry" chore x
    [ "$rc" -eq 3 ] || { echo "first exit $rc, not 3" >&2; return 1; }
    touch "$out/ok"
    run "$tmp/work/retry" --setup "$out"
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [ -e "$tmp/work/retry-x/built.txt" ] || return 1
}

case_setup_refuses_a_foreign_directory() {
    mkrepo here
    mkrepo there
    refused foreign "$tmp/work/here" "not a worktree of here" --setup "$tmp/work/there"
}

case_says_when_the_repo_has_no_recipe() {
    mkrepo bare $'other:\n\t@true\n'
    run "$tmp/work/bare" chore x
    [ "$rc" -eq 0 ] || { echo "exit $rc: $err" >&2; return 1; }
    [[ "$err" == *"no 'worktree-setup' recipe"* ]] || { echo "no notice: $err" >&2; return 1; }
}

case_links_fieldkit_when_the_main_checkout_has_it() {
    mkrepo linked
    mkdir "$tmp/kit"
    ln -s "$tmp/kit" "$tmp/work/linked/.fieldkit"
    run "$tmp/work/linked" chore x
    [ "$(readlink -f "$out/.fieldkit")" = "$tmp/kit" ] || { echo "link is wrong" >&2; return 1; }
    mkrepo unlinked
    run "$tmp/work/unlinked" chore x
    [ ! -e "$out/.fieldkit" ] || { echo "a link was made with none to copy" >&2; return 1; }
}

for case_fn in $(declare -F | awk '$3 ~ /^case_/ {print $3}'); do
    name="${case_fn#case_}"
    # Outside an `if`, so set -e holds inside the case: a failed setup command
    # fails it instead of being ignored.
    set +e
    (
        set -e
        "$case_fn"
    )
    status=$?
    set -e
    if [ "$status" -eq 0 ]; then
        echo "test-new-worktree: ok - ${name//_/ }"
    else
        echo "test-new-worktree: FAILED - ${name//_/ }" >&2
        failed=1
    fi
done
exit "$failed"
