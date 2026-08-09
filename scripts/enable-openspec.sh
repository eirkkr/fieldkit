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

schema="review-gated"

# The schema directory and its templates/ must be real directories: OpenSpec
# discovers schemas with a directory check that a symlink fails, so linking
# the folder itself yields "Unknown schema". Linking the files inside a real
# folder works, and keeps the kit the single source. See ADR 034.
mkdir -p "openspec/schemas/$schema/templates"
for src in ".fieldkit/schemas/$schema/schema.yaml" \
    ".fieldkit/schemas/$schema/templates/"*.md; do
    rel="${src#.fieldkit/schemas/$schema/}"
    dest="openspec/schemas/$schema/$rel"
    # ../ back to the repo root: 3 levels from the schema dir, 4 from
    # templates/.
    case "$rel" in
    */*) up="../../../../" ;;
    *) up="../../../" ;;
    esac
    target="$up.fieldkit/schemas/$schema/$rel"
    if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$target" ]; then
        echo "Already linked openspec/schemas/$schema/$rel, no change"
    else
        ln -sfn "$target" "$dest"
        echo "Linked openspec/schemas/$schema/$rel"
    fi
done

if grep -qx "schema: $schema" openspec/config.yaml; then
    echo "openspec/config.yaml already selects $schema, no change"
else
    sed -i "s/^schema: .*/schema: $schema/" openspec/config.yaml
    grep -qx "schema: $schema" openspec/config.yaml ||
        sed -i "1i schema: $schema" openspec/config.yaml
    echo "Set schema: $schema in openspec/config.yaml"
fi

echo "Commit openspec/ and .claude/skills/openspec-* to finish enabling OpenSpec."
