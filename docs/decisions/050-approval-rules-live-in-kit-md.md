# 050 - Approval rules live in KIT.md, not in the conventions docs

## Decision

`conventions/*.md` no longer say what an agent must ask before doing. Every
such rule is stated once, in `KIT.md`'s Always-on table and the bullets
under it. A conventions doc keeps the fact that makes the rule sensible -
closing an issue ends a thread someone may be relying on, a force-push
replaces commits a reviewer has read - and leaves out who approves.

This amends [042](042-regate-issue-filing.md), which had
`conventions/github.md` restate the issue gate and put its out-of-scope line
as "a choice put to the human".

Force-pushing a branch with an open PR joins the table as `ask first`.

## Reason

`KIT.md` already says the conventions docs are read by humans and agents
alike, and that its own process vocabulary stays out of them. The approval
sentences broke that without using the vocabulary: "filing an issue is
confirmed first, unless the person asked for one" is addressed to an agent,
and a human reading it is the person in question. It surfaced when a new
force-push rule was written the same way, copying the voice already there.

The restated rules were also a second copy. [039](039-always-on-gate-table.md)
made the table the place a gate is read from; a conventions doc repeating
one has to be changed with it, and 042 had to edit both.

Rejected: rewording the approval sentences to be neutral ("is confirmed
first") while keeping them. A passive hides who confirms without making the
sentence useful to a human, and the second copy stays.

## Consequences

- An agent that reads `github.md` or `git.md` without `KIT.md` in context
  finds no approval rules. `KIT.md` is always-on wherever the kit is
  imported, so this needs the import to be missing.
- A new approval rule is a table row or a bullet in `KIT.md`. A conventions
  doc gains at most the fact behind it.
- Other agent-addressed wording went the same way: `specs.md` names the
  reviewer and the implementer where it said "a human" and "the agent".
- Mentions of what Claude Code's hooks and skills do stay. They describe
  tooling, and are true for any reader.
