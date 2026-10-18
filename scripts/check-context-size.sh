#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Check the text the kit puts into consumer sessions stays within a byte
# budget: KIT.md, which every consumer @-imports; each convention hub, such
# as the Python one a Python consumer imports; and the description of each
# skill the kit links, which Claude Code lists in every session unless the
# skill sets `disable-model-invocation: true`. The total is what a consumer
# importing everything loads, the upper bound. Each skill's name and the
# listing's formatting are not counted. Over budget, a PR trims, moves a
# rule behind the load-on-demand table, or raises the budget here, where the
# reviewer sees it.
budget=8726

fail() {
    echo "check-context-size: $1" >&2
    exit 1
}

# A skill's frontmatter description, joined to one line as Claude Code shows
# it: inline, quoted, or a `>`/`|` block, blank lines included. Prints
# nothing for a skill Claude Code doesn't list, and exits non-zero when it
# finds no frontmatter or no description, so a skill it can't read fails
# the check instead of counting as 0 bytes.
description() {
    awk '
        { sub(/\r$/, "") }
        NR == 1 { if ($0 == "---") { front = 1; next } else exit }
        $0 == "---" { closed = 1; exit }
        more && (/^[[:space:]]/ || /^$/) {
            line = $0
            sub(/^[[:space:]]+/, "", line)
            if (line != "") text = text (text != "" ? " " : "") line
            next
        }
        { more = 0 }
        /^disable-model-invocation:[[:space:]]*true[[:space:]]*$/ { disabled = 1 }
        /^description:/ {
            value = $0
            sub(/^description:[[:space:]]*/, "", value)
            more = 1
            if (value ~ /^[>|][0-9+-]*([[:space:]]+#.*)?$/) next
            if (value ~ /^".*"$/ || value ~ /^\047.*\047$/) value = substr(value, 2, length(value) - 2)
            text = value
        }
        END {
            if (!closed || (!disabled && text == "")) exit 1
            if (!disabled) printf "%s", text
        }
    ' "$1"
}

total=0
for file in "$kit/KIT.md" "$kit"/conventions/*/README.md; do
    [ -f "$file" ] || fail "missing ${file#"$kit"/}"
    # An @-import pulls in a file this check doesn't count.
    if grep -q '^@' "$file"; then
        fail "${file#"$kit"/} @-imports a file this check doesn't count"
    fi
    bytes="$(wc -c <"$file")"
    total=$((total + bytes))
done
for skill in "$kit"/skills/*/SKILL.md "$kit"/python-skills/*/SKILL.md; do
    [ -f "$skill" ] || fail "no skill matches ${skill#"$kit"/}"
    text="$(description "$skill")" || fail "no description read from ${skill#"$kit"/}"
    bytes="$(printf '%s' "$text" | wc -c)"
    total=$((total + bytes))
done

if [ "$total" -gt "$budget" ]; then
    fail "$total bytes always loaded, over the $budget-byte budget (about $((total / 4)) tokens)"
fi
echo "check-context-size: $total of $budget bytes always loaded (about $((total / 4)) tokens)"
