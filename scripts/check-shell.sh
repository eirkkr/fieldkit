#!/usr/bin/env bash
set -euo pipefail
kit="$1"

# Lint the kit's shell scripts with shellcheck and check their formatting
# with shfmt, whose style is in .editorconfig. With --fix, format them in
# place instead. Some of these scripts run in every consumer repo - the
# pre-commit hook, the statusline, the enable-*.sh scripts.
#
# Scripts are found by shebang, not extension, since hooks/pre-commit has
# none. Tracked files only, so node_modules/ stays out.
shellcheck=(uvx --from shellcheck-py@0.11.0.1 shellcheck)
shfmt=(uvx --from shfmt-py@4.2.0 shfmt)

cd "$kit"

files=()
while IFS= read -r -d '' file; do
    # Symlinks are skipped: the files they point at are listed themselves,
    # or are a consumer's, and some dangle in a checkout.
    [ -f "$file" ] && [ ! -L "$file" ] || continue
    first=""
    IFS= read -r first <"$file" || true
    if [[ "$first" =~ ^\#!.*[/[:space:]](ba)?sh([[:space:]]|$) ]]; then
        files+=("$file")
    fi
done < <(git ls-files -z)

if [ "${#files[@]}" -eq 0 ]; then
    echo "check-shell: found no shell scripts" >&2
    exit 1
fi

if [ "${2:-}" = "--fix" ]; then
    "${shfmt[@]}" --write "${files[@]}"
    exit 0
fi

# Each tool's failure is caught rather than left to set -e, so both always
# run and every failure prints a check-shell: line.
status=0

if out="$("${shellcheck[@]}" --format=gcc "${files[@]}" 2>&1)"; then
    echo "check-shell: shellcheck passed on ${#files[@]} scripts"
else
    printf '%s\n' "$out" | sed 's/^/check-shell: /' >&2
    echo "check-shell: shellcheck failed" >&2
    status=1
fi

if out="$("${shfmt[@]}" --list "${files[@]}" 2>&1)" && [ -z "$out" ]; then
    echo "check-shell: shfmt passed on ${#files[@]} scripts"
else
    printf '%s\n' "$out" | sed 's/^/check-shell: not formatted: /' >&2
    echo "check-shell: shfmt failed - run \`just fix\` to format" >&2
    status=1
fi

exit "$status"
