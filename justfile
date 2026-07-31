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
    @"{{ justfile_directory() }}/scripts/register-stop-hook.sh" "{{ justfile_directory() }}"

# Set this clone's fix command for the format-drift Stop hook (per clone).
setup:
    git config fieldkit.fixCommand "just fix"
    @echo "Set fieldkit.fixCommand - the Stop hook will run 'just fix' at turn end"

# Bump the pinned openspec CLI and regenerate repo-skills/ from it.
openspec-refresh:
    @"{{ justfile_directory() }}/scripts/openspec-refresh.sh" "{{ justfile_directory() }}"

# Lint all markdown.
check:
    uvx rumdl@0.2.26 check .

# Auto-fix markdown issues.
fix:
    uvx rumdl@0.2.26 check --fix .
