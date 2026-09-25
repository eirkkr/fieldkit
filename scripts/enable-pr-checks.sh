#!/usr/bin/env bash
set -euo pipefail

# Write a workflow that fails any PR whose branch name or title breaks the
# kit's rules, by calling the kit's reusable pr-conventions workflow. Run from
# a consumer repo's root.

if [ ! -e ./.fieldkit ]; then
    echo "./.fieldkit not found - see the kit README's consumer-repo setup" >&2
    exit 1
fi

# The kit's own GitHub repo, so a fork's consumers call the fork.
url="$(git -C .fieldkit remote get-url origin)"
kit="$(printf '%s\n' "$url" | sed -E 's#^(https://github\.com/|git@github\.com:)##; s#\.git$##')"
if ! printf '%s\n' "$kit" | grep -qE '^[^/]+/[^/]+$'; then
    echo "Couldn't read a GitHub owner/repo from the kit's origin ($url)" >&2
    exit 1
fi

dest=".github/workflows/pr-conventions.yml"
content="name: PR conventions

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

jobs:
  pr-conventions:
    uses: $kit/.github/workflows/pr-conventions.yml@main
    with:
      kit-repository: $kit
"

if [ -f "$dest" ] && [ "$(cat "$dest")" = "$(printf '%s' "$content")" ]; then
    echo "Already wrote $dest, no change"
elif [ -e "$dest" ]; then
    echo "$dest already exists with other content - move it aside first" >&2
    exit 1
else
    mkdir -p .github/workflows
    printf '%s' "$content" > "$dest"
    echo "Wrote $dest"
fi

# The caller an earlier version of this script wrote, for the branch-name
# check alone. The kit no longer has that workflow, so the caller would fail;
# removed only when it is exactly what was written, never a repo's own file.
old=".github/workflows/branch-name.yml"
old_content="name: Branch name

on: pull_request

jobs:
  branch-name:
    uses: $kit/.github/workflows/branch-name.yml@main
    with:
      kit-repository: $kit
"
if [ -f "$old" ] && [ "$(cat "$old")" = "$(printf '%s' "$old_content")" ]; then
    rm "$old"
    echo "Removed $old, which pr-conventions.yml replaces"
fi

echo "Commit .github/workflows/ to finish enabling the PR checks."
