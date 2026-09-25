# List available commands.
default:
    @just --list

# Set up skills, agents, statusline, and Claude settings.
install:
    @"{{ justfile_directory() }}/scripts/install-openspec.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/link-skills.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/link-agents.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/link-statusline.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/register-dir.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/disable-attribution.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/register-statusline.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/register-hooks.sh" "{{ justfile_directory() }}"

# Set this clone's fix command for the format-drift Stop hook (per clone).
setup:
    git config fieldkit.fixCommand "just fix"
    @echo "Set fieldkit.fixCommand - the Stop hook will run 'just fix' at turn end"

# Bump the pinned openspec CLI and regenerate repo-skills/ from it.
openspec-refresh:
    @"{{ justfile_directory() }}/scripts/openspec-refresh.sh" "{{ justfile_directory() }}"

# Run all checks: the linters, plus this branch's name and its PR's title.
check: lint check-branch-name check-pr-title

# Lint markdown and check the vendored skills still carry their overlays.
lint: rumdl check-overlays

# Lint all markdown.
rumdl:
    #!/usr/bin/env bash
    set -euo pipefail
    uvx rumdl@0.2.26 check . 2>&1 | sed '/^$/d; s/^/rumdl: /'

# Check each vendored skill still ends with its overlay.
check-overlays:
    @"{{ justfile_directory() }}/scripts/check-skill-overlays.sh" "{{ justfile_directory() }}"

# Check this branch's name against git.md - the PR's branch in CI, else the checked-out one.
check-branch-name:
    @"{{ justfile_directory() }}/scripts/check-branch-name.sh" "{{ justfile_directory() }}"

# Check this branch's PR title against git.md's commit rules - the PR's in CI, else the open one.
check-pr-title:
    @"{{ justfile_directory() }}/scripts/check-pr-title.sh" "{{ justfile_directory() }}"

# Auto-fix markdown issues.
fix:
    uvx rumdl@0.2.26 check --fix .
