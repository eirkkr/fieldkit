#!/usr/bin/env bash
set -euo pipefail
kit="$1"
uv run python "$kit/scripts/pin_worktree_base.py"
