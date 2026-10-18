# Written records

Issues, ADRs, specs and convention docs outlive the conversation that produced them, and are acted on by someone who never saw it.

## The body stands alone

- An issue, ADR or spec is read without the conversation that produced it, so everything needed to act on it belongs in the body: the decisions still open, the docs that must change alongside the code, the reasoning behind a choice that looks arbitrary, and anything the conversation built that the reader would otherwise rebuild - a prompt or script that worked, where each change has to go, what it cost.
- Two tests before filing. A plan to brief whoever picks the work up means something is missing from the body. And read as the person who will act on it, the body is finished when they could start the first step without asking.
- A later finding that changes what the body says is edited into the body, not left in a comment beneath it, where someone acting on the body alone would miss it.

## Exemptions and violations

- An exemption list records why each entry is exempt, in terms of the rule it escapes, so the reason could be used to refuse an entry. One describing what the code does instead ("uses the raw driver", "runs at startup") cannot be audited, and the list grows by precedent.
- Known violations of a convention live in the issue tracker, not in the convention document - the document outlives them, and a stale list of files reads as permission.

## Convention docs

A convention doc is read by people as well as agents. It states git and GitHub mechanics as plain facts, and leaves the vocabulary of the agent's instructions - act-then-show, gate, dispatching a subagent - to `KIT.md` and the skill files that carry them out, so the doc reads without either open.
