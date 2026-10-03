# 051 - Move the record-writing rules on demand

## Decision

Four of `KIT.md`'s Always-on bullets move to a new load-on-demand doc,
`conventions/records.md`, reached by a new row in the Load on Demand table:
"Writing an issue, ADR, spec or convention doc, or an exemption list".

The four are the rules that bear only on writing a record:

- everything needed to act on an issue, ADR or spec belongs in its body;
- a later finding that changes the body is edited into the body;
- an exemption list records why each entry is exempt, in terms of the rule
  it escapes;
- known violations of a convention live in the issue tracker, not in the
  convention document.

Two neighbouring rules stay always-on: that a count or a claim about a
file's contents is re-derived from the tree, and that reading part of a file
is not reading it.

## Reason

`KIT.md` is resident in every session of every consumer repo
([039](039-always-on-gate-table.md)). The four bullets came to 221 words,
and a session that writes no issue, ADR, spec or convention doc carried them
for nothing.

[039](039-always-on-gate-table.md) rejected demoting the gate rules, on the
ground [025](025-skill-routing-stated-always-on.md) gave: a pointer is only
consulted once the agent suspects it needs a lookup, which is too late for a
rule about whether to ask. That does not hold here. These rules apply at a
moment the agent knows it has reached - it is about to write the record -
which is the same kind of trigger the `decisions.md` and `specs.md` rows
already rely on.

Alternatives rejected:

- **Fold each rule into the doc for its artifact** - `github.md` for issues,
  `decisions.md` for ADRs, `specs.md` for specs. The body rules cover all
  three, so they would be stated three times, the drift
  [019](019-git-on-demand-via-skills.md) rejected. One doc costs one
  resident row.
- **Move the re-derived-count rule too.** It also covers commit messages,
  and a commit goes through the `push` skill, which does not read
  `records.md`. Behind this pointer the rule would stop reaching the
  commonest place a stale figure gets written.
- **Move the rule that `conventions/*.md` state facts and keep `KIT.md`'s
  vocabulary out.** [050](050-approval-rules-live-in-kit-md.md) leans on
  `KIT.md` saying so, and the rule names `KIT.md`'s own terms, which a
  conventions doc cannot use.

## Consequences

- `KIT.md` drops from 1375 words to 1170, and its Always-on section from
  1179 to 958. `conventions/records.md` is 262 words, read only when a
  record is written.
- The four rules now depend on the row being followed, the weaker guarantee
  [002](002-always-on-vs-load-on-demand.md) accepted for every on-demand
  doc. Filing an issue or recording an ADR matches two rows, and both docs
  are read.
- `records.md` is written for a human reader as well, like the other
  conventions docs: it says what a finished body contains, not what an
  agent should check.
- A new rule about writing a record goes into `records.md`, not back into
  `KIT.md`.
