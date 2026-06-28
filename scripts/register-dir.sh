#!/usr/bin/env bash
set -euo pipefail
uv run python - "$1" <<'EOF'
import json, pathlib, sys
p = pathlib.Path.home() / '.claude' / 'settings.json'
d = json.loads(p.read_text()) if p.exists() else {}
a = d.setdefault('permissions', {}).setdefault('additionalDirectories', [])
new_dir = sys.argv[1] not in a
if new_dir:
    a.append(sys.argv[1])
new_mem = d.get('autoMemoryEnabled') is not False
if new_mem:
    d['autoMemoryEnabled'] = False
if new_dir or new_mem:
    p.write_text(json.dumps(d, indent=2))
msgs = []
suffix = ' in ~/.claude/settings.json'
msgs.append(('Registered ' + sys.argv[1] + suffix) if new_dir else ('Already registered' + suffix + ', no change'))
msgs.append('Disabled autoMemory' + suffix if new_mem else 'autoMemory already disabled' + suffix + ', no change')
print('\n'.join(msgs))
EOF
