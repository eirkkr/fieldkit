# List available commands.
default:
    @just --list

# Lint all markdown.
check:
    uvx pymarkdownlnt@0.9.38 scan -r .

# Auto-fix markdown issues.
fix:
    uvx pymarkdownlnt@0.9.38 fix -r .
