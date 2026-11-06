# 066 - Writing style follows the primary reader

## Decision

A file's style is set by who reads it first.

- **Agents first** - `KIT.md`, `CLAUDE.md`, `docs/reviews.md`, and the bodies of `skills/` and `python-skills/`: telegraphic. Drop articles and filler, fold clauses with a colon, use fragments in bullets and steps.
- **People first** - `conventions/`, ADRs, `README.md`: concise full sentences. Short, positive, no padding, but grammatical, so a person can follow and review it.

In both, a rule's conditions and exceptions ("unless", "only when", "even if") stay explicit. A fragment that could be read two ways is written as a full sentence. Step order, "Done when" criteria, headings other files cite and strings a script matches are never shortened away. Skill frontmatter descriptions are budgeted ([ADR 060](060-budget-the-always-loaded-context.md)) and written tight in either style.

The rule is in `conventions/records.md`, "Style follows the primary reader".

## Reason

Every always-loaded byte costs context in every session of every consumer repo, and skill bodies load each time a skill fires. Agents read fragments as well as sentences, so their files lose nothing by going telegraphic.

People read the convention docs, review the ADRs and follow the setup guides. Fragments cost them effort and invite misreading, so those files keep full sentences.

The conditions rule exists because dropped connectives are where a telegraphic rule goes wrong: "merge after CI, ask first" can be read two ways, and an agent that misreads an exception over- or under-applies the rule.

Measured when adopted: telegraphic wording cut `KIT.md` by about 4% beyond a prose trim, and skill bodies by about 4%. Most of the savings came from removing restatement and moving rules behind the load-on-demand table, not from grammar, so the style is a modest lever to use where agents are the readers, not a reason to cut rules.

Rejected:

- **Telegraphic everywhere.** Saves little more in on-demand files and costs the people who read them.
- **Full sentences everywhere.** Keeps the always-loaded files longer than they need to be.
- **A lint for it.** Telegraphic style is not machine-checkable, so it stays a written rule, as [ADR 013](013-style-rules-in-tooling-not-context.md) allows where tooling can't do the job.

## Consequences

- A file with both audiences, such as a skill whose steps a person also follows, takes the style of the first reader named in its header or its location above. When unsure, use full sentences.
- Editing an agent-first file, match its telegraphic style; editing a people-first one, keep sentences.
- Moving a file between the two groups is a style change too.
