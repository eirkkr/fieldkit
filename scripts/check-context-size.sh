#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Check the text the kit puts into every consumer session stays within a
# byte budget: KIT.md, which a consumer @-imports; the Python hub, which a
# Python consumer imports; and the description of each skill the kit
# links, since Claude Code lists every linked skill's description in every
# session. Each byte here is paid in every session of every consumer, and
# the total grew a bullet at a time with nothing measuring it. Over budget,
# a PR trims, moves a rule behind the load-on-demand table, or raises the
# budget here, where the reviewer sees it.
budget=9282

# A frontmatter description, inline or as a folded `>-` block, joined to one
# line as Claude Code shows it.
description() {
    awk '
        NR == 1 && /^---$/ { front = 1; next }
        front && /^---$/ { exit }
        front && block && /^[[:space:]]/ { sub(/^[[:space:]]+/, ""); text = text (text ? " " : "") $0; next }
        front && block { exit }
        front && /^description:/ {
            sub(/^description:[[:space:]]*/, "")
            if ($0 ~ /^[>|]-?$/) { block = 1; next }
            text = $0; exit
        }
        END { printf "%s", text }
    ' "$1"
}

total=0
for file in "$kit/KIT.md" "$kit/conventions/python/README.md"; do
    total=$((total + $(wc -c <"$file")))
done
for skill in "$kit"/skills/*/SKILL.md "$kit"/python-skills/*/SKILL.md; do
    total=$((total + $(description "$skill" | wc -c)))
done

if [ "$total" -gt "$budget" ]; then
    echo "check-context-size: $total bytes always loaded, over the $budget-byte budget (about $((total / 4)) tokens)" >&2
    exit 1
fi
echo "check-context-size: $total of $budget bytes always loaded (about $((total / 4)) tokens)"
