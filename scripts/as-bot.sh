#!/usr/bin/env bash
set -euo pipefail

# Run a command as the bot account: its token from
# ~/.config/bot-account/token, and none of the user's own GitHub logins.
# The setup steps and what each setting does are in
# conventions/bot-account.md (step 7).
#
#   as-bot.sh command [arguments]    for example: as-bot.sh claude

if [ "$#" -eq 0 ]; then
    echo "usage: as-bot.sh command [arguments]" >&2
    exit 2
fi

dir="$HOME/.config/bot-account"
token="$(cat "$dir/token" 2>/dev/null)" || token=""
if [ -z "$token" ]; then
    echo "as-bot: no bot token in $dir/token" >&2
    exit 1
fi

unset GITHUB_TOKEN GH_ENTERPRISE_TOKEN GITHUB_ENTERPRISE_TOKEN
unset GIT_ASKPASS SSH_ASKPASS GIT_CONFIG_PARAMETERS
export GH_TOKEN="$token"
export GH_HOST=github.com
export GH_CONFIG_DIR="$dir/gh"
export GIT_SSH_COMMAND=false
export GIT_CONFIG_COUNT=4
export GIT_CONFIG_KEY_0=credential.helper GIT_CONFIG_VALUE_0=
export GIT_CONFIG_KEY_1=credential.https://github.com.helper GIT_CONFIG_VALUE_1='!gh auth git-credential'
export GIT_CONFIG_KEY_2=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_2=git@github.com:
export GIT_CONFIG_KEY_3=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_3=ssh://git@github.com/

exec "$@"
