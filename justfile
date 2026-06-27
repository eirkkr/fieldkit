# List available commands.
default:
    @just --list

# Set up slash commands and Claude settings.
install:
    mkdir -p ~/.claude/commands
    ln -sf "{{ justfile_directory() }}/commands/kit-reconcile.md" ~/.claude/commands/kit-reconcile.md
    @echo "Linked /kit-reconcile into ~/.claude/commands"
    @python3 -c "import json,pathlib,sys; p=pathlib.Path.home()/'.claude'/'settings.json'; d=json.loads(p.read_text()) if p.exists() else {}; s=d.setdefault('permissions',{}); a=s.setdefault('additionalDirectories',[]); new=sys.argv[1] not in a; new and a.append(sys.argv[1]); new and p.write_text(json.dumps(d,indent=2)); print(('Registered '+sys.argv[1]+' in ~/.claude/settings.json') if new else 'Already registered in ~/.claude/settings.json, no change')" "{{ justfile_directory() }}"

# Lint all markdown.
check:
    uvx pymarkdownlnt@0.9.38 scan -r .

# Auto-fix markdown issues.
fix:
    uvx pymarkdownlnt@0.9.38 fix -r .
