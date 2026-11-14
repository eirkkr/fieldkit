#!/usr/bin/env bash
set -euo pipefail

# Start the Test workflow on the current branch's pushed head. A push to a PR
# runs test.yml as attempt 1, which skips its job; a re-run is attempt 2,
# which runs it. So this re-runs the latest run for the head. The run uses
# what the remote holds, so refuse a branch whose local head is not that: the
# check would land on a commit nobody meant.
workflow="test.yml"

branch="$(git branch --show-current)"
if [[ -z "$branch" ]]; then
    echo "ci: detached HEAD - check out the PR's branch" >&2
    exit 1
fi
if ! fetch_error="$(git fetch --quiet origin "$branch" 2>&1)"; then
    echo "ci: cannot fetch '$branch' from origin - is it pushed? $fetch_error" >&2
    exit 1
fi
head="$(git rev-parse HEAD)"
if [[ "$head" != "$(git rev-parse "origin/$branch")" ]]; then
    echo "ci: '$branch' differs from origin/$branch - push it first" >&2
    exit 1
fi

# --jq prints "<id> <status>", or "null null" when the head has no run yet.
if ! run="$(gh run list --workflow "$workflow" --event pull_request --commit "$head" \
    --limit 1 --json databaseId,status --jq '.[0] | "\(.databaseId) \(.status)"' 2>&1)" ||
    [[ -z "$run" || "$run" == "null null" ]]; then
    echo "ci: no $workflow run for $head - is the PR open? Its first run starts on a push." >&2
    [[ "$run" == "null null" || -z "$run" ]] || echo "ci: gh said: $run" >&2
    exit 1
fi
id="${run% *}"
if [[ "${run#* }" != completed ]]; then
    echo "ci: the latest $workflow run ($id) is still ${run#* } - wait for it, then run again" >&2
    exit 1
fi
gh run rerun "$id"
echo "ci: re-running $workflow ($id) at $head"
echo "ci: follow it with 'gh pr checks --watch'"
