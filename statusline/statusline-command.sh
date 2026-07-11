#!/usr/bin/env bash
# Claude Code status line: colored usage percentages, rate limits, cost, code velocity

input=$(cat)

# ── Colors ──
BLUE='\033[34m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
ORANGE='\033[38;2;255;140;0m'
RED='\033[31m'
MAGENTA='\033[35m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

# ── Color-by-usage helper: blue < 10%, green 10-50%, yellow 50-75%, orange 75-90%, red >= 90% ──
usage_color() {
  local pct="$1"
  if [ "$pct" -ge 90 ]; then printf '%s' "$RED"
  elif [ "$pct" -ge 75 ]; then printf '%s' "$ORANGE"
  elif [ "$pct" -ge 50 ]; then printf '%s' "$YELLOW"
  elif [ "$pct" -ge 10 ]; then printf '%s' "$GREEN"
  else printf '%s' "$BLUE"; fi
}

# ── Time-remaining helper: unix epoch seconds -> "3h40m" / "2d5h" ──
time_remaining() {
  local reset_epoch="$1"
  [ -z "$reset_epoch" ] && return
  local now_epoch diff
  now_epoch=$(date +%s)
  diff=$(( reset_epoch - now_epoch ))
  [ "$diff" -le 0 ] && return
  local days=$(( diff / 86400 ))
  local hours=$(( (diff % 86400) / 3600 ))
  local mins=$(( (diff % 3600) / 60 ))
  if [ "$days" -gt 0 ]; then printf '%dd%dh' "$days" "$hours"
  elif [ "$hours" -gt 0 ]; then printf '%dh%dm' "$hours" "$mins"
  else printf '%dm' "$mins"; fi
}

# ── Parse JSON fields ──
model=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
cost=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
lines_add=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
lines_del=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')

five_hour_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_hour_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
weekly_pct=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
weekly_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# ── Git info ──
branch=""
repo=""
if [ -n "$cwd" ]; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  repo=$(basename "$(git -C "$cwd" --no-optional-locks rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null)
fi

# ── Context usage ──
if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  ctx_part="Ctx $(usage_color "$used_int")${used_int}%${RESET}"
else
  ctx_part="Ctx ${DIM}--%${RESET}"
fi

# ── 5-hour rate limit ──
if [ -n "$five_hour_pct" ]; then
  five_hour_int=$(printf '%.0f' "$five_hour_pct")
  five_hour_part="5h $(usage_color "$five_hour_int")${five_hour_int}%${RESET}"
  five_hour_left=$(time_remaining "$five_hour_reset")
  [ -n "$five_hour_left" ] && five_hour_part="${five_hour_part} ${DIM}${five_hour_left}${RESET}"
fi

# ── Weekly (7-day) rate limit ──
if [ -n "$weekly_pct" ]; then
  weekly_int=$(printf '%.0f' "$weekly_pct")
  weekly_part="7d $(usage_color "$weekly_int")${weekly_int}%${RESET}"
  weekly_left=$(time_remaining "$weekly_reset")
  [ -n "$weekly_left" ] && weekly_part="${weekly_part} ${DIM}${weekly_left}${RESET}"
fi

# ── Cost ──
cost_part="${YELLOW}$(printf '$%.2f' "$cost")${RESET}"

# ── Code velocity ──
velocity="${GREEN}+${lines_add}${RESET} ${RED}-${lines_del}${RESET}"

# ── Groups: git (repo, branch, velocity) | context (model, ctx) | usage (5h, 7d, cost) ──
git_group=""
[ -n "$repo" ] && git_group="${BOLD}${YELLOW}${repo}${RESET}"
[ -n "$branch" ] && git_group="${git_group:+$git_group }${BOLD}${CYAN}${branch}${RESET}"
git_group="${git_group:+$git_group ${DIM}|${RESET} }${velocity}"

context_group="${MAGENTA}${model}${RESET} ${DIM}|${RESET} ${ctx_part}"

usage_group=""
[ -n "$five_hour_part" ] && usage_group="${five_hour_part}"
[ -n "$weekly_part" ] && usage_group="${usage_group:+$usage_group ${DIM}|${RESET} }${weekly_part}"
usage_group="${usage_group:+$usage_group ${DIM}|${RESET} }${cost_part}"

out="$git_group"
out="${out:+$out ${DIM}|${RESET} }${context_group}"
out="${out} ${DIM}|${RESET} ${usage_group}"

printf '%b' "$out"
