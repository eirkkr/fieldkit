# List available commands.
default:
    @just --list

# Symlink kit slash commands into the user-level Claude commands dir.
install:
    mkdir -p ~/.claude/commands
    ln -sf "{{ justfile_directory() }}/commands/kit-reconcile.md" ~/.claude/commands/kit-reconcile.md
    @echo "Linked /kit-reconcile into ~/.claude/commands"

# Lint all markdown.
check:
    uvx pymarkdownlnt@0.9.38 scan -r .

# Auto-fix markdown issues.
fix:
    uvx pymarkdownlnt@0.9.38 fix -r .
