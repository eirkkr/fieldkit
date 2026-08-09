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

# Re-apply the kit's overlays. rsync --delete has just reverted repo-skills/
# to stock upstream, so anything the kit adds has to go back on here - see
# ADR 034. Each repo-skills-overlay/<skill>.md is appended to that skill's
# SKILL.md; a stock skill with no overlay file is left alone.
for overlay in "$kit"/repo-skills-overlay/*.md; do
    [ -e "$overlay" ] || continue
    name="$(basename "$overlay" .md)"
    target="$kit/repo-skills/$name/SKILL.md"
    if [ ! -f "$target" ]; then
        echo "Overlay $name.md has no matching skill in repo-skills/ - skipped" >&2
        continue
    fi
    printf '\n' >>"$target"
    cat "$overlay" >>"$target"
    echo "Applied overlay to $name"
done

after="$(cd "$kit/repo-skills" && ls -d openspec-*/ 2>/dev/null | sort)"

new="$(comm -13 <(printf '%s' "$before") <(printf '%s' "$after"))"
if [ -n "$new" ]; then
    echo "New skill dir(s) added: $new"
    echo "Adopting repos must re-run .fieldkit/scripts/enable-openspec.sh to pick them up."
fi

echo "Refreshed repo-skills/ from openspec $("$openspec" --version)"
