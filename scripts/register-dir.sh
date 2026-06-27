#!/usr/bin/env bash
set -euo pipefail
python3 - "$1" <<'EOF'
import json, pathlib, sys
p = pathlib.Path.home() / '.claude' / 'settings.json'
d = json.loads(p.read_text()) if p.exists() else {}
a = d.setdefault('permissions', {}).setdefault('additionalDirectories', [])
new = sys.argv[1] not in a
if new:
    a.append(sys.argv[1])
    p.write_text(json.dumps(d, indent=2))
suffix = ' in ~/.claude/settings.json'
print(('Registered ' + sys.argv[1] + suffix) if new else ('Already registered' + suffix + ', no change'))
EOF
