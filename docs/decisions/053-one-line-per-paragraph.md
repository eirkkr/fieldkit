# 053 - One line per paragraph

## Decision

Markdown in this repo is not hard-wrapped. Each paragraph and list item is a single line, and `rumdl`'s MD013 enforces it: `line-length = 0` with `reflow = true` and `reflow-mode = "normalize"` in `.rumdl.toml`. `just fix` joins a wrapped paragraph; `just rumdl` reports one.

## Reason

A hard wrap puts a line break wherever the column limit fell, so editing a sentence re-breaks its neighbours and the diff shows the reflow rather than the change. It also splits phrases across lines, which is why KIT.md has to warn that a line-based `grep` over wrapped prose proves nothing. Editors soft-wrap for the human reader, so the break buys nothing.

Rejected:

- **`sentence-per-line`.** Diffs are cleaner still, but it breaks a paragraph into many lines, which keeps the `grep` problem for phrases that span sentences and reads oddly in the raw file.
- **Leaving the 80-column default.** Keeps the churn and the split phrases.

## Consequences

- One commit reflows every Markdown file outside the excluded vendored skills. Run `git blame --ignore-rev` on it to see through to the earlier change.
- `repo-skills-overlay/*.md` is reflowed too, so each overlay was re-appended to its vendored `repo-skills/*/SKILL.md`; `just check-overlays` compares them byte for byte. An overlay edit still needs that re-append.
- KIT.md does not state the rule, since a consumer's own `rumdl` config decides whether its prose is wrapped. It only tells an agent to read that config rather than assume a width, and its audit-by-phrase advice stays for wrapped consumers.
- Commit messages and PR bodies keep their own wrapping rules ([047](047-enforce-commit-messages.md)); this covers Markdown files only.
