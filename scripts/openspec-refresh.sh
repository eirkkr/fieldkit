#!/usr/bin/env bash
set -euo pipefail
kit="$1"

before="$(cd "$kit/repo-skills" && ls -d openspec-*/ 2>/dev/null | sort)"

npm install --prefix "$kit" --save-exact "@fission-ai/openspec@latest"

openspec="$kit/node_modules/.bin/openspec"
"$openspec" config set delivery skills

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
(cd "$tmp" && "$openspec" init --tools claude >/dev/null)

rsync -a --delete "$tmp/.claude/skills/" "$kit/repo-skills/"

after="$(cd "$kit/repo-skills" && ls -d openspec-*/ 2>/dev/null | sort)"

new="$(comm -13 <(printf '%s' "$before") <(printf '%s' "$after"))"
if [ -n "$new" ]; then
    echo "New skill dir(s) added: $new"
    echo "Adopting repos must re-run .fieldkit/scripts/enable-openspec.sh to pick them up."
fi

echo "Refreshed repo-skills/ from openspec $("$openspec" --version)"
