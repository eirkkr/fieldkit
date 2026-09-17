#!/usr/bin/env bash
set -euo pipefail

if [ ! -e ./.fieldkit ]; then
    echo "./.fieldkit not found - see the kit README's consumer-repo setup" >&2
    exit 1
fi

if [ ! -f pyproject.toml ]; then
    echo "pyproject.toml not found - run this from a Python repo's root" >&2
    exit 1
fi

mkdir -p .claude/skills
for skill_dir in .fieldkit/python-skills/*/; do
    name="$(basename "$skill_dir")"
    dest=".claude/skills/$name"
    target="../../.fieldkit/python-skills/$name"
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
        echo "Already linked .claude/skills/$name, no change"
    elif [ -e "$dest" ] && [ ! -L "$dest" ]; then
        # A repo-local skill of the same name - replacing it would discard
        # whatever the repo has there, so leave the call to a human.
        echo ".claude/skills/$name is a real directory, not a link - remove it to adopt the kit's copy" >&2
    else
        ln -sfn "$target" "$dest"
        echo "Linked .claude/skills/$name"
    fi
done

# Prune links this script made for skills that were renamed or removed.
for dest in .claude/skills/*; do
    [ -L "$dest" ] || continue
    target="$(readlink "$dest")"
    case "$target" in
    ../../.fieldkit/python-skills/*)
        [ -d "$dest" ] && continue
        rm "$dest"
        echo "Removed stale skill link $dest ($target no longer exists)"
        ;;
    esac
done

if ! grep -qE '^check( |:)' justfile 2>/dev/null; then
    echo "No 'check' recipe in ./justfile - update-deps runs 'just check' after a bump" >&2
fi

echo "Commit the .claude/skills links to finish enabling the Python skills."
