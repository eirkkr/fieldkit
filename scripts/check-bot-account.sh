#!/usr/bin/env bash
set -euo pipefail

# Check a GitHub bot account's token against one repo with read-only calls.
# The steps for making the bot and its token are in
# conventions/bot-account.md, which also says what each result means.
#
#   check-bot-account.sh owner/name
#
# The token is read from a hidden prompt, or from GH_TOKEN when that is
# already set, and never from an argument, so it stays out of the process
# list. Do not run it as GH_TOKEN=<token> check-bot-account.sh: the shell
# records that line in its history. Exit 0 when the token does not have
# admin on the repo, 1 when it does, and 2 on any error: a usage error, no
# token, a refused token, a failed account or repo lookup, a response with
# no permissions, an interrupt, or a missing gh. A failed protection lookup
# is only a note.

die() {
    echo "check-bot-account: $1" >&2
    exit 2
}

repo="${1:-}"
owner="${repo%%/*}"
name="${repo#*/}"
if [ "$#" -ne 1 ] || [[ ! "$repo" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] ||
    [ "$owner" = . ] || [ "$owner" = .. ] || [ "$name" = . ] || [ "$name" = .. ]; then
    die "usage: check-bot-account.sh owner/name"
fi

command -v gh >/dev/null 2>&1 || die "gh not found - install the GitHub CLI first"

# Ctrl-C at the token prompt is an error exit like any other.
trap 'echo >&2; exit 2' INT

echo "Checking the bot's token against $repo. The steps for making the bot and"
echo "its token are in conventions/bot-account.md (.fieldkit/conventions/ in a"
echo "consumer repo)."
if [ -z "${GH_TOKEN:-}" ]; then
    # read returns non-zero on a last line with no newline, token included.
    read -r -s -p "Bot token: " GH_TOKEN || [ -n "$GH_TOKEN" ] || die "no token given"
    echo
fi
[ -n "$GH_TOKEN" ] || die "no token given"
export GH_TOKEN
# This check is about github.com; a GH_HOST in the environment would send it
# to another host, under another login.
export GH_HOST=github.com

errf="$(mktemp)"
trap 'rm -f "$errf"' EXIT

# The last gh call's error output, on one line, with the token blanked.
err() {
    local e
    e="$(<"$errf")"
    e="${e//"$GH_TOKEN"/***}"
    e="$(printf '%s' "$e" | tr '\n' ' ' | tr -d '\000-\010\013-\037\177')"
    printf '%s' "${e% }"
}

if ! login="$(gh api user -q .login 2>"$errf")"; then
    case "$(err)" in
        *"HTTP 401"*) die "GitHub refused the token (HTTP 401): it is mistyped, expired or revoked. Make a new one and run this again." ;;
        *) die "could not look up the token's account: $(err)" ;;
    esac
fi
[[ "$login" =~ ^[A-Za-z0-9-]+$ ]] || die "GitHub returned a login this check cannot read"
echo "pass: the token belongs to $login"
echo "      That must be the bot's login. If it is yours, this is the wrong token."

# permissions is absent from the response for some token kinds; that is an
# error, not a pass. The fields are joined with the unit separator, which
# read does not treat as whitespace, so an empty field stays empty.
query='[(.permissions.admin | tostring), (.permissions.push | tostring), .default_branch, (.private | tostring), .owner.type] | join("\u001f")'
if ! info="$(gh api "repos/$repo" -q "$query" 2>"$errf")"; then
    case "$(err)" in
        *"HTTP 404"*)
            cat >&2 <<EOF
check-bot-account: GitHub answered 404 Not Found for repos/$repo.
The token cannot see that repo. If the name is right, the usual causes are:
  - the token was made without the repo scope
  - (organization) the organization blocks classic tokens
  - the bot has not accepted its invitation, or is not yet on the team
    that has access to the repo
EOF
            exit 2
            ;;
        *) die "could not look up $repo: $(err)" ;;
    esac
fi
IFS=$'\x1f' read -r admin push branch private owner_type <<<"$info"

case "$admin" in
    true) status=1 ;;
    false) status=0 ;;
    *) die "repos/$repo returned no permissions for this token, so admin cannot be checked" ;;
esac

if [ "$status" -eq 0 ]; then
    echo "pass: $login does not have admin on $repo"
    if [ "$push" = true ]; then
        echo "      Good: it cannot delete the repo or change its protection rules."
    else
        echo "note: $login cannot push to $repo, so Claude could not open a PR as it."
        echo "      Check that the invitation is accepted, the team has Write, the"
        echo "      token is approved, and a classic token has the repo scope."
    fi
elif [ "$owner_type" = User ]; then
    echo "fail: $login has admin on $repo"
    echo "      Only the owner has admin on a personal repo, so this is the owner's"
    echo "      token, not the bot's. Make a token as the bot and run this again."
else
    echo "fail: $login has admin on $repo"
    echo "      Lower its role to Write. Check it is a Member, not an Owner, that no"
    echo "      team gives it Admin, and that the organization's base permission is"
    echo "      not Admin."
fi

# Protection is shown, not judged. A branch protection rule and a ruleset are
# separate APIs, so either one counts, and each lookup that fails is named
# with GitHub's message. A branch name with characters that would need
# URL-encoding is not looked up, and is not printed.
show_protection() {
    local protected="" rules="" protected_err="" rules_err=""
    case "$branch" in
        "" | *[!A-Za-z0-9._/-]*)
            echo "note: the default branch name is empty or has characters this check does not look up;"
            echo "      check its protection under the repo's Settings > Rulesets"
            return
            ;;
    esac
    protected="$(gh api "repos/$repo/branches/$branch" -q .protected 2>"$errf")" || protected_err="$(err)"
    rules="$(gh api "repos/$repo/rules/branches/$branch" -q length 2>"$errf")" || rules_err="$(err)"

    if [ "$protected" = true ] || { [[ "$rules" =~ ^[0-9]+$ ]] && [ "$rules" -gt 0 ]; }; then
        echo "note: the default branch $branch is protected (a protection rule or ruleset applies)"
        echo "      This check cannot tell whether it stops $login; test 1 in the doc does."
    elif [ "$protected" = false ] && [ "$rules" = 0 ]; then
        echo "note: the default branch $branch has no branch protection rule or ruleset,"
        echo "      so $login can push to, force-push and delete it."
        if [ "$private" = true ]; then
            echo "      $repo is private: on a free plan it most likely cannot have either."
        fi
    else
        if [ -n "$protected_err" ]; then
            echo "note: the branch protection lookup (repos/$repo/branches/$branch) failed: $protected_err"
        fi
        if [ -n "$rules_err" ]; then
            echo "note: the ruleset lookup (repos/$repo/rules/branches/$branch) failed: $rules_err"
        fi
        if [ -z "$protected_err$rules_err" ]; then
            echo "note: the protection lookups gave answers this check cannot read" \
                "(protected: '$(printf '%s' "$protected" | LC_ALL=C tr -cd '[:print:]')'," \
                "rulesets: '$(printf '%s' "$rules" | LC_ALL=C tr -cd '[:print:]')')"
        fi
        if [ "$private" = true ] && [ -n "$rules_err" ]; then
            echo "      $repo is private, and on a free plan a private repo most likely"
            echo "      cannot have protection, which would explain a failed ruleset lookup."
        fi
        echo "      Treat $branch as unprotected until test 1 in the doc is refused."
    fi
}
show_protection

if [ "$status" -ne 0 ] && [ "$owner_type" = User ]; then
    echo "Done: make a token as the bot, then run this again."
elif [ "$status" -ne 0 ]; then
    echo "Done: fix the role above, then run this again."
elif [ "$push" = true ]; then
    echo "Done: the token has no admin and can push. Next, test it by hand and"
    echo "run Claude as the bot (steps 6 and 7 in the doc)."
else
    echo "Done: the token has no admin, but see the note above before going on."
fi
exit "$status"
