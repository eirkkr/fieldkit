#!/usr/bin/env bash
set -euo pipefail
kit="$(cd "$1" && pwd -P)"

# Test hooks/pretooluse-worktree-edit.py against throwaway repos: a bare
# remote and a clone of it for each, and for a consumer a throwaway kit its
# `.fieldkit` points at. The hook takes "the kit" to be the checkout it sits
# in, so each case runs a copy of the hook placed in a throwaway kit, not the
# one in $kit. Prints a line per case, prefixed with the recipe name, and
# exits 1 if any failed.

base="$(mktemp -d)"
trap 'rm -rf "$base"' EXIT
cd "$base"

# Nothing from the machine's git config may reach the throwaway repos.
# A GIT_DIR exported by a hook or `rebase --exec` would send every git call
# here to that repo, not the throwaway ones.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null
export GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t
failed=0
hook=""

# mkrepo <name> [<default branch>]: a clone at $tmp/work/<name> with one
# commit on the default branch (main unless given), pushed to a bare remote,
# holding a tracked file and a .gitignore naming an ignored file.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
mkrepo() {
    local name="$1" dir="$tmp/work/$1" default="${2:-main}"
    git init -q --bare -b "$default" "$tmp/remotes/$name.git"
    git clone -q "$tmp/remotes/$name.git" "$dir" 2>/dev/null
    printf 'ignored.txt\n.claude/worktrees/\n.fieldkit\n' >"$dir/.gitignore"
    echo one >"$dir/tracked.txt"
    git -C "$dir" add .gitignore tracked.txt
    git -C "$dir" commit -q -m init
    git -C "$dir" push -q origin "$default"
    git -C "$dir" remote set-head origin "$default"
}

# mkkit <name>: a repo that is the kit, holding a copy of the hook under test,
# which later calls run.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
mkkit() {
    mkrepo "$1"
    mkdir "$tmp/work/$1/hooks"
    cp "$kit/hooks/pretooluse-worktree-edit.py" "$kit/hooks/conventions.py" "$tmp/work/$1/hooks/"
    hook="$tmp/work/$1/hooks/pretooluse-worktree-edit.py"
}

# mkconsumer <name>: a repo with a `.fieldkit` link to its own throwaway kit
# <name>-kit, which also becomes the hook under test.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
mkconsumer() {
    mkkit "$1-kit"
    mkrepo "$1"
    ln -s "$tmp/work/$1-kit" "$tmp/work/$1/.fieldkit"
}

# call <tool> <path> <cwd>: run the hook on that tool call, setting $out and $rc.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
call() {
    local key=file_path
    [ "$1" = NotebookEdit ] && key=notebook_path
    send "$(printf '{"tool_name":"%s","tool_input":{"%s":"%s"},"cwd":"%s"}' "$1" "$key" "$2" "$3")"
}

# send <payload>: run the hook on a raw payload, setting $out and $rc.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
send() {
    rc=0
    out="$(printf '%s' "$1" | python3 "$hook" 2>"$tmp/err")" || rc=$?
}

# denied [<fragment>...]: the last call was refused, its text holding each fragment.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
denied() {
    [ "$rc" -eq 0 ] || {
        echo "exit $rc: $(cat "$tmp/err")" >&2
        return 1
    }
    [[ "$out" == *'"permissionDecision": "deny"'* ]] || {
        echo "not refused: '$out'" >&2
        return 1
    }
    local fragment
    for fragment in "$@"; do
        [[ "$out" == *"$fragment"* ]] || {
            echo "refusal lacks '$fragment': $out" >&2
            return 1
        }
    done
}

# allowed: the last call was let through, with no output.
# shellcheck disable=SC2329 # only called from the case_ functions, which the loop at the foot calls by name
allowed() {
    [ "$rc" -eq 0 ] && [ -z "$out" ] || {
        echo "refused or failed (exit $rc): '$out' $(cat "$tmp/err")" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_a_tracked_file_in_a_consumer() {
    mkconsumer api
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_a_tracked_file_in_the_kit() {
    mkkit lib
    call Edit "$tmp/work/lib/tracked.txt" "$tmp/work/lib"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_a_write_of_a_new_file_in_a_new_directory() {
    mkconsumer api
    call Write "$tmp/work/api/docs/new/page.md" "$tmp/work/api"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_a_notebook_edit() {
    mkconsumer api
    call NotebookEdit "$tmp/work/api/notes.ipynb" "$tmp/work/api"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_a_default_branch_read_from_origin_head() {
    mkkit lib
    mkrepo trunk master
    ln -s "$tmp/work/lib" "$tmp/work/trunk/.fieldkit"
    call Edit "$tmp/work/trunk/tracked.txt" "$tmp/work/trunk"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_reads_the_default_branch_from_config_first() {
    mkconsumer api
    git -C "$tmp/work/api" switch -q -c dev
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    allowed || return 1
    git -C "$tmp/work/api" config fieldkit.defaultBranch dev
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_a_kit_file_from_a_consumer_and_says_to_ask() {
    mkconsumer api
    call Edit "$tmp/work/api/.fieldkit/tracked.txt" "$tmp/work/api"
    denied "ask the reviewer to open a session in a kit worktree" "fieldkit.allowMainEdits" || return 1
    [[ "$out" != *new-worktree.sh* ]] || {
        echo "a kit file's refusal names the script: $out" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_does_not_say_to_ask_for_a_file_in_the_session_repo() {
    mkconsumer api
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied || return 1
    [[ "$out" != *"ask the reviewer"* ]] || {
        echo "the ordinary refusal says to ask: $out" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_names_the_consumer_script_and_the_rest_of_the_rule() {
    mkconsumer api
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied "\`.fieldkit/scripts/new-worktree.sh <type> <description>\`" "EnterWorktree" \
        "Exit 3" "--existing <branch>" "fieldkit.allowMainEdits"
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_names_the_kits_own_script_path_in_the_kit() {
    mkkit lib
    call Edit "$tmp/work/lib/tracked.txt" "$tmp/work/lib"
    denied "\`scripts/new-worktree.sh <type> <description>\`" "Exit 3" "--existing <branch>" || return 1
    [[ "$out" != *.fieldkit/scripts* ]] || {
        echo "the kit's refusal names the consumer path: $out" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_file_in_a_linked_worktree() {
    mkconsumer api
    git -C "$tmp/work/api" worktree add -q --no-track -b chore/x "$tmp/work/api-x" origin/main
    call Edit "$tmp/work/api-x/tracked.txt" "$tmp/work/api-x"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_sends_a_session_in_a_worktree_to_its_own_copy_of_the_file() {
    mkconsumer api
    git -C "$tmp/work/api" worktree add -q --no-track -b chore/x "$tmp/work/api-x" origin/main
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api-x"
    denied "already in a worktree of that repo" "$tmp/work/api-x/tracked.txt" "fieldkit.allowMainEdits" || return 1
    [[ "$out" != *"Create a worktree first"* ]] || {
        echo "a session in a worktree is told to make another: $out" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_sends_a_kit_session_editing_a_consumer_file_to_the_reviewer() {
    mkconsumer api
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api-kit"
    denied "ask the reviewer to open a session in a worktree of that repo" "fieldkit.allowMainEdits" || return 1
    [[ "$out" != *".fieldkit/scripts"* ]] || {
        echo "a kit session is told to run the consumer's script: $out" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_gives_the_ordinary_text_when_the_session_is_in_no_repo() {
    mkconsumer api
    call Edit "$tmp/work/api/tracked.txt" "$tmp/loose"
    denied "Create a worktree first" || return 1
    [[ "$out" != *"ask the reviewer to open"* ]] || {
        echo "a session in no repo is told to ask: $out" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_repo_with_no_commit_yet() {
    mkkit lib
    git init -q -b main "$tmp/work/fresh"
    ln -s "$tmp/work/lib" "$tmp/work/fresh/.fieldkit"
    call Write "$tmp/work/fresh/README.md" "$tmp/work/fresh"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_does_not_run_a_repos_fsmonitor_command() {
    mkconsumer api
    git -C "$tmp/work/api" config core.fsmonitor "touch $tmp/ran; echo"
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied || return 1
    [ ! -e "$tmp/ran" ] || {
        echo "the repo's fsmonitor command ran" >&2
        return 1
    }
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_quotes_the_repo_path_in_the_switch_command() {
    mkconsumer "sp ace"
    call Edit "$tmp/work/sp ace/tracked.txt" "$tmp/loose"
    denied "git -C '$tmp/work/sp ace' config fieldkit.allowMainEdits true"
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_refuses_when_the_switch_value_is_not_a_boolean() {
    mkconsumer api
    git -C "$tmp/work/api" config fieldkit.allowMainEdits maybe
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_linked_worktree_even_on_the_default_branch() {
    mkconsumer api
    git -C "$tmp/work/api" worktree add -q --no-track -b chore/x "$tmp/work/api-x" origin/main
    git -C "$tmp/work/api" config fieldkit.defaultBranch chore/x
    call Edit "$tmp/work/api-x/tracked.txt" "$tmp/work/api-x"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_an_ignored_kit_file_reached_through_the_link() {
    mkconsumer api
    call Write "$tmp/work/api/.fieldkit/ignored.txt" "$tmp/work/api"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_file_in_a_linked_worktree_of_the_kit() {
    mkkit lib
    git -C "$tmp/work/lib" worktree add -q --no-track -b chore/x "$tmp/work/lib-x" origin/main
    call Edit "$tmp/work/lib-x/tracked.txt" "$tmp/work/lib-x"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_file_in_a_claude_code_worktree() {
    mkconsumer api
    git -C "$tmp/work/api" worktree add -q --no-track -b worktree-w "$tmp/work/api/.claude/worktrees/w" origin/main
    call Edit "$tmp/work/api/.claude/worktrees/w/tracked.txt" "$tmp/work/api"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_an_ignored_file_in_the_main_checkout() {
    mkconsumer api
    call Write "$tmp/work/api/ignored.txt" "$tmp/work/api"
    allowed || return 1
    call Write "$tmp/work/api/.claude/worktrees/anything/file.txt" "$tmp/work/api"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_non_default_branch() {
    mkconsumer api
    git -C "$tmp/work/api" switch -q -c chore/mine
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_detached_head() {
    mkconsumer api
    git -C "$tmp/work/api" checkout -q --detach
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_file_outside_any_repo() {
    mkconsumer api
    echo x >"$tmp/loose/note.txt"
    call Edit "$tmp/loose/note.txt" "$tmp/work/api"
    allowed || return 1
    call Write "$tmp/loose/new/dir/note.txt" "$tmp/work/api"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_a_repo_that_does_not_use_the_kit() {
    mkkit lib
    mkrepo plain
    call Edit "$tmp/work/plain/tracked.txt" "$tmp/work/plain"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_ignores_other_tools() {
    mkconsumer api
    send "$(printf '{"tool_name":"Bash","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$tmp/work/api/tracked.txt" "$tmp/work/api")"
    allowed || return 1
    send "$(printf '{"tool_name":"Read","tool_input":{"file_path":"%s"},"cwd":"%s"}' "$tmp/work/api/tracked.txt" "$tmp/work/api")"
    allowed
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_allows_when_the_switch_is_on() {
    mkconsumer api
    git -C "$tmp/work/api" config fieldkit.allowMainEdits true
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    allowed || return 1
    git -C "$tmp/work/api" config fieldkit.allowMainEdits false
    call Edit "$tmp/work/api/tracked.txt" "$tmp/work/api"
    denied
}

# shellcheck disable=SC2329 # called by name from the loop at the foot
case_lets_through_payloads_it_cannot_read() {
    mkconsumer api
    local payload
    for payload in 'not json' '[]' '{}' '{"tool_name":"Edit"}' '{"tool_name":"Edit","tool_input":[]}' \
        '{"tool_name":"Edit","tool_input":{"file_path":5}}' '{"tool_name":"Edit","tool_input":{"file_path":""}}'; do
        send "$payload"
        allowed || {
            echo "payload: $payload" >&2
            return 1
        }
    done
}

for case_fn in $(declare -F | awk '$3 ~ /^case_/ {print $3}'); do
    name="${case_fn#case_}"
    # Outside an `if`, so set -e holds inside the case: a failed setup command
    # fails it instead of being ignored.
    set +e
    (
        set -e
        # Each case gets a scratch directory of its own, so repo names can repeat.
        tmp="$base/$name"
        mkdir -p "$tmp/remotes" "$tmp/work" "$tmp/loose"
        "$case_fn"
    )
    status=$?
    set -e
    if [ "$status" -eq 0 ]; then
        echo "test-worktree-edit-hook: ok - ${name//_/ }"
    else
        echo "test-worktree-edit-hook: FAILED - ${name//_/ }" >&2
        failed=1
    fi
done
exit "$failed"
