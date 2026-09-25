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

# Lint all markdown, and check vendored skills' overlays and the branch-name hook's rules.
check: check-overlays check-branch-rules
    uvx rumdl@0.2.26 check .

# Check each vendored skill still ends with its overlay.
check-overlays:
    @"{{ justfile_directory() }}/scripts/check-skill-overlays.sh" "{{ justfile_directory() }}"

# Check the branch-name hook still reads its prefixes and length cap out of git.md.
check-branch-rules:
    @python3 "{{ justfile_directory() }}/hooks/pretooluse-branch-name.py" --rules > /dev/null || (echo "hooks/pretooluse-branch-name.py couldn't read the prefixes or length cap from conventions/git.md's Branches bullets" >&2; exit 1)

# Check this branch's name against git.md - the PR's branch in CI (branch-name.yml), else the checked-out one.
check-branch-name:
    #!/usr/bin/env bash
    set -euo pipefail
    branch="${GITHUB_HEAD_REF:-$(git branch --show-current)}"
    # Detached HEAD, or the default branch, which the rules don't name.
    if [ -z "$branch" ] || [ "$branch" = main ]; then exit 0; fi
    python3 "{{ justfile_directory() }}/hooks/pretooluse-branch-name.py" --name "$branch"

# Auto-fix markdown issues.
fix:
    uvx rumdl@0.2.26 check --fix .
