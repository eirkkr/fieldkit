#!/usr/bin/env bash
set -euo pipefail

if [ ! -e ./.fieldkit ]; then
    echo "./.fieldkit not found - see the kit README's consumer-repo setup" >&2
    exit 1
fi

if ! command -v openspec >/dev/null 2>&1; then
    echo "openspec not on PATH - see the kit README's consumer-repo setup" >&2
    exit 1
fi

if [ -d openspec ]; then
    echo "openspec/ already exists, no change"
else
    openspec init --tools none
    echo "Created openspec/"
fi

mkdir -p .claude/skills
for skill_dir in .fieldkit/repo-skills/openspec-*/; do
    name="$(basename "$skill_dir")"
    dest=".claude/skills/$name"
    target="../../.fieldkit/repo-skills/$name"
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
        echo "Already linked .claude/skills/$name, no change"
    else
        ln -sfn "$target" "$dest"
        echo "Linked .claude/skills/$name"
    fi
done

echo "Commit openspec/ and .claude/skills/openspec-* to finish enabling OpenSpec."
