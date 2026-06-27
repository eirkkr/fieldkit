# List available commands.
default:
    @just --list

# Set up slash commands and Claude settings.
install:
    @"{{ justfile_directory() }}/scripts/link-commands.sh" "{{ justfile_directory() }}"
    @"{{ justfile_directory() }}/scripts/register-dir.sh" "{{ justfile_directory() }}"

# Lint all markdown.
check:
    uvx pymarkdownlnt@0.9.38 scan -r .

# Auto-fix markdown issues.
fix:
    uvx pymarkdownlnt@0.9.38 fix -r .
