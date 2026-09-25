#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# The branch-name hook reads its prefixes and length limit out of
# conventions/git.md's Branches bullets, and skips a check it can't read. So a
# rewording that stops a bullet parsing would silently switch that check off;
# this catches it.
if ! rules="$(python3 "$kit/hooks/pretooluse-branch-name.py" --rules)"; then
    echo "check-branch-rules: couldn't read the prefixes or length limit from conventions/git.md's Branches bullets" >&2
    exit 1
fi
echo "check-branch-rules: git.md's rules parse ($(echo "$rules" | tr '\n' ';' | sed 's/;$//; s/;/; /'))"
