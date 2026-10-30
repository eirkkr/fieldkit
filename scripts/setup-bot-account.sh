#!/usr/bin/env bash
set -euo pipefail

# Walk the user through giving Claude a limited GitHub account, then check
# the bot's token against one repo with read-only calls. See
# conventions/bot-account.md for what each step is for.
#
#   GH_TOKEN=<bot token> setup-bot-account.sh owner/name
#
# GH_TOKEN is read from the environment, or from a hidden prompt when unset,
# and never from an argument, so it stays out of the process list and shell
# history. Exit 0 when the token does not have admin on the repo, 1 when it
# does, and 2 on a usage error, no token, an invalid token, an API error or
# a missing gh.

die() {
    echo "setup-bot-account: $1" >&2
    exit 2
}

repo="${1:-}"
owner="${repo%%/*}"
name="${repo#*/}"
if [ "$#" -ne 1 ] || [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] ||
    [ "$owner" = . ] || [ "$owner" = .. ] || [ "$name" = . ] || [ "$name" = .. ]; then
    die "usage: setup-bot-account.sh owner/name"
fi

command -v gh >/dev/null 2>&1 || die "gh not found - install the GitHub CLI first"

# Wait for Enter between steps when a person is at the terminal; a piped
# run prints the steps and goes on.
pause() {
    if [ -t 0 ]; then
        read -r -p "Press Enter when done... " _ || die "aborted"
    fi
}

step() {
    printf '\n%s\n' "$1"
    pause
}

cat <<EOF
Steps for a limited GitHub account for Claude. Do them in a browser logged
in as the bot, except the invite, which the repo's owner sends.
EOF
step "1. Create a GitHub account for the bot, with its own email address."
step "2. As the owner of $repo, invite the bot as a collaborator with the write role. For an organization repo, add it as a member with write on the repo instead. Never give it admin."
step "3. Accept the invitation as the bot."
step "4. As the bot, create the token. Personal repo: a classic token with the repo scope and no workflow scope. Organization repo: a fine-grained token limited to the repos it works in, with Contents, Pull requests and Issues set to read and write and no Administration."
step "5. Protect the default branch with a ruleset or branch protection rule that requires a pull request and blocks force pushes and deletion."
step "6. Paste the token at the prompt below, or set GH_TOKEN before running this script. It is checked here and not stored."

if [ -z "${GH_TOKEN:-}" ]; then
    # read returns non-zero on a last line with no newline, token included.
    read -r -s -p "Bot token: " GH_TOKEN || [ -n "$GH_TOKEN" ] || die "no token given"
    echo
fi
[ -n "$GH_TOKEN" ] || die "no token given"
export GH_TOKEN

errf="$(mktemp)"
trap 'rm -f "$errf"' EXIT

# Read-only call; a failure is an error (exit 2), not a failed check. stderr
# is kept out of the value, and the token is blanked from what is printed.
api() {
    local out
    if ! out="$(gh api "$@" 2>"$errf")"; then
        out="$(cat "$errf")"
        die "gh api $1 failed: ${out//"$GH_TOKEN"/***}"
    fi
    printf '%s\n' "$out"
}

login="$(api user -q .login)"
echo "pass: the token belongs to $login"

# permissions is absent from the response for some token kinds; treat that as
# an error rather than as no admin.
admin="$(api "repos/$repo" -q '.permissions.admin | tostring')"
branch="$(api "repos/$repo" -q .default_branch)"

case "$admin" in
    true) status=1 ;;
    false) status=0 ;;
    *) die "repos/$repo returned no permissions for this token" ;;
esac

if [ "$status" -eq 0 ]; then
    echo "pass: $login does not have admin on $repo"
else
    echo "fail: $login has admin on $repo - lower its role to write"
fi

# Protection is shown, not judged, and a lookup that fails or cannot be read
# says so rather than guessing: a branch protection rule and a ruleset are
# separate APIs, so either one counts. A branch name with characters that
# would need URL-encoding is not looked up.
protected=""
rules=""
case "$branch" in
    *[!A-Za-z0-9._/-]*) ;;
    *)
        protected="$(gh api "repos/$repo/branches/$branch" -q .protected 2>/dev/null || true)"
        rules="$(gh api "repos/$repo/rules/branches/$branch" -q length 2>/dev/null || true)"
        ;;
esac

if [ "$protected" = "true" ] || { [[ "$rules" =~ ^[0-9]+$ ]] && [ "$rules" -gt 0 ]; }; then
    echo "note: the default branch $branch is protected"
elif [ "$protected" = "false" ] && [ "$rules" = "0" ]; then
    echo "note: the default branch $branch has no protection rule or ruleset, so $login can push to it"
else
    echo "note: could not tell whether the default branch $branch is protected"
fi

exit "$status"
