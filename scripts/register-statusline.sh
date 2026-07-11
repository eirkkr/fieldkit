#!/usr/bin/env bash
set -euo pipefail
kit="$1"
uv run python "$kit/scripts/register_statusline.py"
