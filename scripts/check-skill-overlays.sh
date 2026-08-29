#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# `repo-skills/<name>/SKILL.md` is generated - the stock upstream skill with
# `repo-skills-overlay/<name>.md` appended by openspec-refresh.sh - and both
# halves are checked in. So an overlay edited without regenerating leaves the
# vendored skill serving the old text, which still loads and still reads
# plausibly; the drift is invisible until an agent follows a retired rule.
# That is what happened to the review-gate overlay when the stage became the
# unit of merge (ADR 041): the source said one thing and the skill an agent
# actually reads said the retired thing, and it took an agent following the
# retired rule to surface it.
status=0

for overlay in "$kit"/repo-skills-overlay/*.md; do
    [ -e "$overlay" ] || continue
    name="$(basename "$overlay" .md)"
    target="$kit/repo-skills/$name/SKILL.md"

    if [ ! -f "$target" ]; then
        echo "$name: repo-skills/$name/SKILL.md is missing" >&2
        status=1
        continue
    fi

    bytes="$(wc -c <"$overlay" | tr -d '[:space:]')"
    if tail -c "$bytes" "$target" | diff -q - "$overlay" >/dev/null; then
        echo "$name: overlay is current"
    else
        echo "$name: repo-skills/$name/SKILL.md does not end with repo-skills-overlay/$name.md" >&2
        status=1
    fi
done

if [ "$status" -ne 0 ]; then
    cat >&2 <<'MSG'

The vendored skill and its overlay have drifted. Re-apply the overlays with
`just openspec-refresh`, or append the overlay by hand if the pinned openspec
version should not move.
MSG
fi

exit "$status"
