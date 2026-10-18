# 060 - Budget the always-loaded context in CI

## Decision

`just check-context-size`, part of `just lint`, adds up the bytes the kit puts into every consumer session and fails when the total passes a budget set in `scripts/check-context-size.sh`. The total covers `KIT.md`, `conventions/python/README.md`, and the `description` of each skill in `skills/` and `python-skills/`, which Claude Code lists in every session where the skill is linked. The budget started at 8862 bytes, the total at the time (8057) plus 10%.

## Reason

Everything a consumer `@`-imports, and every linked skill's description, is in context for every session of every consumer repo. [ADR 002](002-always-on-vs-load-on-demand.md) kept that set small by moving situational rules behind the load-on-demand table, but nothing measured it afterwards, and `KIT.md` grew by a bullet or two with most rule changes. Each addition was reasonable on its own. Together they were never weighed. In line with [ADR 013](013-style-rules-in-tooling-not-context.md), a check does this better than a written rule asking authors to keep the file short.

The budget is not a cap. A PR that goes over it trims text, moves a rule behind the load-on-demand table, or raises the number in the script, and any of these shows in the diff for the reviewer to weigh.

Before the budget was set, the always-loaded text was trimmed: redundant text in `KIT.md` was removed, the rule on the voice of convention docs moved to `conventions/records.md`, the advice on searching hard-wrapped prose was dropped (see the note on [ADR 053](053-one-line-per-paragraph.md)), and sentences that only explained a rule, or restated another, were cut. Together these cut `KIT.md` from 7941 to 6530 bytes.

Rejected:

- **Counting tokens.** Exact, but it needs a tokenizer or an API call in CI, where every other check runs offline with nothing to install. Bytes track tokens closely enough for a budget, and the check prints a rough token figure (bytes / 4) next to them.
- **A written length limit in `KIT.md` or a convention doc.** It would cost context itself, and an agent applies it unreliably (ADR 013).
- **Checking each consumer's own `CLAUDE.md`.** That text is the consumer's to weigh against its own needs. The kit's share is the part one kit PR grows in every consumer at once, and checking it here covers all of them.

## Consequences

- Consumers need no change: they read the same `KIT.md` and skills, which the kit's CI now checks.
- The vendored OpenSpec skills are not counted. They are opt-in and are being removed.
- A new skill, or a longer description, counts against the budget like a `KIT.md` bullet.
