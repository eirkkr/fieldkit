# 058 - Compact tables

## Decision

Markdown tables in this repo are not column-aligned. Each cell has one space of padding either side, `| a | b |`, and a delimiter row is `| --- |` per column, whatever the column's width. `rumdl`'s MD060 enforces the cells: `style = "compact"` in `.rumdl.toml`, where it was `"aligned"`. `just fix` strips the padding from an aligned table; `just rumdl` reports one.

## Reason

An aligned table pads every cell to its column's widest entry, so lengthening one cell re-pads every row of the table and the diff shows the realignment rather than the change. An ADR whose title is longer than any before it re-pads every row of the register. The same reasoning took hard wraps out of prose ([053](053-one-line-per-paragraph.md)): editors and renderers lay the table out for the reader, so the padding buys nothing.

The delimiter row matters too. Compact style accepts a delimiter of any length, so a padded `| -------- |` left over from alignment would pass the lint while still needing a rewrite whenever its column's width changed. The conversion shortened every one to `---`, and new tables follow the existing ones. The lint doesn't check this, but nothing breaks if one slips through.

Rejected:

- **`tight`** (`|a|b|`). It has the same diff property, but reads cramped in the raw file and is unlike most hand-written Markdown.
- **`any`.** It leaves the choice to each table, which lets aligned tables back in through `just fix` on an inconsistent one.

## Consequences

- One commit rewrote every table outside the excluded vendored skills. Use `git blame --ignore-rev` on it to see past it to the earlier change.
- Tables are harder to read in the raw file, most of all wide ones like the ADR register. A rendered view or an editor's Markdown preview is the readable form.
- KIT.md's tables are compact now, and that reaches consumers through the import. Their own tables follow their own `rumdl` config.
