# 053 - One line per paragraph

## Decision

Markdown in this repo is not hard-wrapped. Each paragraph and list item is a single line, and `rumdl`'s MD013 enforces it: `line-length = 0` with `reflow = true` and `reflow-mode = "normalize"` in `.rumdl.toml`. `just fix` joins a wrapped paragraph; `just rumdl` reports one.

## Reason

A hard wrap puts a line break wherever the column limit fell, so editing a sentence re-breaks its neighbours and the diff shows the reflow rather than the change. Editors soft-wrap for the human reader, so the break buys nothing.

It also splits phrases across lines. A multi-word `grep` for "line-based search" misses it whenever the wrap fell between the words, and reports the file clean - which is why KIT.md has to warn that a no-hit over wrapped prose proves nothing. With one line per paragraph, a phrase sits on one line wherever it appears, so the search finds it, for an agent auditing prose as much as for a person.

Rejected:

- **`sentence-per-line`.** Diffs are cleaner still, but it breaks a paragraph into many lines, which keeps the `grep` problem for phrases that span sentences and reads oddly in the raw file.
- **Leaving the 80-column default.** Keeps the churn and the split phrases.

## Consequences

- One commit reflows every Markdown file outside the excluded vendored skills. Run `git blame --ignore-rev` on it to see through to the earlier change.
- `repo-skills-overlay/*.md` is reflowed too, so each overlay was re-appended to its vendored `repo-skills/*/SKILL.md`; `just check-overlays` compares them byte for byte. An overlay edit still needs that re-append.
- KIT.md is unchanged. Agents don't run linters and match the surrounding style by eye, which after this change is one line per paragraph, so no instruction is needed; and a consumer's own `rumdl` config decides whether its prose is wrapped, so its audit-by-phrase advice stays.
- Commit messages and PR bodies keep their own wrapping rules ([047](047-enforce-commit-messages.md)); this covers Markdown files only.
