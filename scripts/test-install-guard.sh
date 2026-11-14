#!/usr/bin/env bash
set -euo pipefail
kit="$(cd "$1" && pwd -P)"

# Test scripts/require-main-checkout.sh against a throwaway repo and a linked
# worktree of it, and that the justfile's `install` runs it before anything
# else. Prints a line per case, prefixed with the recipe name, and exits 1 if
# any failed.

base="$(mktemp -d)"
trap 'rm -rf "$base"' EXIT

# Nothing from the machine's git config may reach the throwaway repos, and a
# GIT_DIR exported by a hook would send every git call to another repo.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
failed=0
guard="$kit/scripts/require-main-checkout.sh"

git init -q -b main "$base/main"
git -C "$base/main" commit -q --allow-empty -m init
git -C "$base/main" worktree add -q -b feature/x "$base/linked"
main="$(cd "$base/main" && pwd -P)"

# check <name> <command...>: run the command in a subshell; ok when it succeeds.
check() {
    local name="$1"
    shift
    if (set -e; "$@"); then
        echo "test-install-guard: ok - $name"
    else
        echo "test-install-guard: FAILED - $name" >&2
        failed=1
    fi
}

allowed_in_main() {
    "$guard" "$base/main"
}

refused_in_worktree_naming_main() {
    local err rc=0
    err="$("$guard" "$base/linked" 2>&1)" || rc=$?
    [ "$rc" -eq 1 ] || {
        echo "exit $rc, expected 1" >&2
        return 1
    }
    case "$err" in
        *"$main"*) ;;
        *)
            echo "message does not name $main: $err" >&2
            return 1
            ;;
    esac
}

# The first command of `install` must be the guard, so nothing else runs first.
install_runs_guard_first() {
    local first
    first="$(awk '/^install:/ {found=1; next} found && /^    / {print; exit}' "$kit/justfile")"
    case "$first" in
        *require-main-checkout.sh*) ;;
        *)
            echo "first line of install is: $first" >&2
            return 1
            ;;
    esac
}

check "allowed in the main checkout" allowed_in_main
check "refused in a linked worktree, naming the main checkout" refused_in_worktree_naming_main
check "install runs the guard first" install_runs_guard_first
exit "$failed"
