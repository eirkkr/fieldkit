#!/usr/bin/env bash
set -euo pipefail
kit="$1"
mode="${2:-check}"

# Lint the kit's shell scripts with shellcheck and check their formatting
# with shfmt, whose style is in .editorconfig. With --fix, format them in
# place instead. Several of these run outside the kit - the git hook and the
# enable-*.sh scripts in consumer repos, the statusline in every session.
#
# Scripts are found by the shebang on their first line, not by extension,
# since hooks/pre-commit has none. Tracked files only, so node_modules/
# stays out.
shellcheck=(uvx --from shellcheck-py@0.11.0.1 shellcheck)
shfmt=(uvx --from shfmt-py@4.2.0 shfmt)

fail() {
    echo "check-shell: $1" >&2
    exit 1
}

case "$mode" in
    check | --fix) ;;
    *) fail "unknown argument $mode - expected --fix or nothing" ;;
esac

cd "$kit"

files=()
while IFS= read -r -d '' file; do
    # Defensive: no symlinks are tracked today, and a link's target is
    # either listed itself or outside the kit.
    [ -f "$file" ] && [ ! -L "$file" ] || continue
    first=""
    IFS= read -r first <"$file" || true
    if [[ "$first" =~ ^\#!.*[/[:space:]](ba|da|k)?sh([[:space:]]|$) ]]; then
        files+=("$file")
    fi
done < <(git ls-files -z)

if [ "${#files[@]}" -eq 0 ]; then
    fail "found no shell scripts"
fi

# .editorconfig styles *.sh and hooks/* only. A script anywhere else would
# silently get shfmt's default style, tabs, so it fails here instead.
for file in "${files[@]}"; do
    case "$file" in
        *.sh | hooks/*) ;;
        *) fail "$file is outside .editorconfig's *.sh and hooks/* - give it a .sh extension, or add its path there and here" ;;
    esac
done

if [ "$mode" = "--fix" ]; then
    "${shfmt[@]}" --write -- "${files[@]}"
    exit 0
fi

# Each tool's failure is caught rather than left to set -e, so both always
# run and every failure prints a check-shell: line. stderr is left to the
# terminal rather than captured: uvx reports its downloads there.
status=0

if out="$("${shellcheck[@]}" --format=gcc -- "${files[@]}")"; then
    echo "check-shell: shellcheck passed on ${#files[@]} scripts"
else
    printf '%s\n' "$out" | sed 's/^/check-shell: /' >&2
    echo "check-shell: shellcheck failed" >&2
    status=1
fi

# --list exits 1 when it lists a file, so the exit status alone can't tell
# an unformatted script from a parse error; the list can.
if out="$("${shfmt[@]}" --list -- "${files[@]}")" && [ -z "$out" ]; then
    echo "check-shell: shfmt passed on ${#files[@]} scripts"
elif [ -n "$out" ]; then
    printf '%s\n' "$out" | sed 's/^/check-shell: not formatted: /' >&2
    echo "check-shell: shfmt failed - run \`just fix\` to format" >&2
    status=1
else
    echo "check-shell: shfmt could not run or parse a script - see its error above" >&2
    status=1
fi

exit "$status"
