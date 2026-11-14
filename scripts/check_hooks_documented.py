"""Check that every registered PreToolUse hook is named in the docs.

Run via `just check-hooks-documented`. Takes the kit directory as its one
argument. Each `hooks/pretooluse-*.py` in register_hooks.HOOKS must be named
in conventions/git.md and README.md, and each one on disk must be registered,
so a hook added or renamed cannot go unnamed in the docs. It does not check
the docs' count of hooks.
"""

import pathlib
import sys

import register_hooks

DOCS = ("conventions/git.md", "README.md")


def main() -> int:
    kit = pathlib.Path(sys.argv[1])
    registered = sorted(h.file for h in register_hooks.HOOKS if h.file.startswith("pretooluse-"))
    on_disk = sorted(p.name for p in (kit / "hooks").glob("pretooluse-*.py"))

    problems = [f"{name} is in hooks/ but not in register_hooks.HOOKS" for name in on_disk if name not in registered]
    for doc in DOCS:
        text = (kit / doc).read_text()
        problems += [f"{doc} does not name {name}" for name in registered if name not in text]

    for problem in problems:
        print(f"check-hooks-documented: {problem}", file=sys.stderr)
    if problems:
        return 1
    print(f"check-hooks-documented: {len(registered)} PreToolUse hooks, each named in {' and '.join(DOCS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
