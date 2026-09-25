#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Check a PR title against conventions/git.md's commit rules, as the squash
# subject it becomes once GitHub appends ` (#N)`. In CI the pr-conventions
# workflow passes PR_TITLE and PR_NUMBER; locally the current branch's open
# PR is looked up with gh.
title="${PR_TITLE:-}"
number="${PR_NUMBER:-}"
if [ -z "$number" ]; then
    if ! pr="$(gh pr view --json number,title -q '"\(.number)\t\(.title)"' 2>/dev/null)"; then
        echo "check-pr-title: no open PR for this branch to check"
        exit 0
    fi
    number="${pr%%$'\t'*}"
    title="${pr#*$'\t'}"
fi

if ! reason="$(python3 "$kit/hooks/conventions.py" pr-title "$title" "$number" 2>&1)"; then
    echo "check-pr-title: $reason" >&2
    exit 1
fi
echo "check-pr-title: '$title' (#$number) follows the rules"
