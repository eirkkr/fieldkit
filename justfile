# List available commands.
default:
    @just --list

# Symlink kit slash commands and register kit path in user Claude settings.
install:
    mkdir -p ~/.claude/commands
    ln -sf "{{ justfile_directory() }}/commands/kit-reconcile.md" ~/.claude/commands/kit-reconcile.md
    @echo "Linked /kit-reconcile into ~/.claude/commands"
    @python3 -c "import json,pathlib,sys; p=pathlib.Path.home()/'.claude'/'settings.json'; d=json.loads(p.read_text()) if p.exists() else {}; s=d.setdefault('permissions',{}); a=s.setdefault('additionalDirectories',[]); a.append(sys.argv[1]) if sys.argv[1] not in a else None; p.write_text(json.dumps(d,indent=2))" "{{ justfile_directory() }}"
    @echo "Registered {{ justfile_directory() }} in ~/.claude/settings.json"

# Lint all markdown.
check:
    uvx pymarkdownlnt@0.9.38 scan -r .

# Auto-fix markdown issues.
fix:
    uvx pymarkdownlnt@0.9.38 fix -r .
