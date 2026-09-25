#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Check a PR title against conventions/git.md's commit rules, as the squash
# subject it becomes once GitHub appends ` (#N)`, and its body for the
# `BREAKING CHANGE:` line a `!` title needs. In CI the pr-conventions workflow
# passes PR_TITLE, PR_NUMBER and PR_BODY; locally the current branch's open
# PR is looked up with gh.
title="${PR_TITLE:-}"
number="${PR_NUMBER:-}"
body="${PR_BODY:-}"
if [ -z "$number" ]; then
    if ! number="$(gh pr view --json number -q .number 2>/dev/null)"; then
        echo "check-pr-title: no open PR for this branch to check"
        exit 0
    fi
    title="$(gh pr view --json title -q .title)"
    body="$(gh pr view --json body -q .body)"
fi

if ! reason="$(printf '%s' "$body" | python3 "$kit/hooks/conventions.py" pr-title "$title" "$number" - 2>&1)"; then
    echo "check-pr-title: $reason" >&2
    exit 1
fi
echo "check-pr-title: '$title' (#$number) follows the rules"
