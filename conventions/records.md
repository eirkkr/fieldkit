# Written records

Issues, ADRs, specs and convention docs outlive the conversation that produced them and are acted on by someone who never saw it.

## The body stands alone

- Everything needed to act belongs in the body: open decisions, docs that must change alongside the code, the reasoning behind a choice that looks arbitrary, and whatever the conversation built that the reader would otherwise rebuild (a prompt or script that worked, where each change goes, what it cost).
- Before filing, read it as the person who will act: it is finished when they could start the first step without asking. Planning to brief them means something is missing.
- A later finding that changes the body is edited into it, not left in a comment beneath, where a reader of the body alone would miss it.

## Exemptions and violations

- An exemption list gives each entry's reason in terms of the rule it escapes, so the reason could refuse an entry. A reason describing what the code does instead ("uses the raw driver", "runs at startup") can't be audited, and the list grows by precedent.
- Known violations of a convention live in the issue tracker, not the convention doc: the doc outlives them, and a stale list of files reads as permission.

## Convention docs

A convention doc is read by people as well as agents. It states git and GitHub mechanics as plain facts and leaves the agent-instruction vocabulary (act-then-show, ask first, dispatching a subagent) to `KIT.md` and the skills, so it reads without either open.
