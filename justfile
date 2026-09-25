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

# Lint all markdown, check vendored skills' overlays and the branch-name hook's prefixes.
check: check-overlays check-branch-prefixes
    uvx rumdl@0.2.26 check .

# Check each vendored skill still ends with its overlay.
check-overlays:
    @"{{ justfile_directory() }}/scripts/check-skill-overlays.sh" "{{ justfile_directory() }}"

# Check the branch-name hook still reads the allowed prefixes out of git.md.
check-branch-prefixes:
    @python3 "{{ justfile_directory() }}/hooks/pretooluse-branch-name.py" --prefixes > /dev/null || (echo "hooks/pretooluse-branch-name.py read no prefixes from conventions/git.md's 'Allowed prefixes:' bullet" >&2; exit 1)

# Auto-fix markdown issues.
fix:
    uvx rumdl@0.2.26 check --fix .
