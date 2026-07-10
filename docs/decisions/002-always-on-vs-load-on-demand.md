# 002 - Tier conventions into always-on and load-on-demand

## Decision

`CLAUDE.md` splits the conventions into two tiers: broadly-relevant ones
(`workflow`, `git`, `style`) are `@`-imported so they are always in context;
situational ones (`github`, `decisions`) are listed in a trigger table and read
on demand only when the matching action comes up.

## Reason

`@`-imports are inlined into context every session, so importing every
convention would carry tokens for rules that rarely apply (GitHub actions, ADR
authoring) into every session. Loading everything always-on was rejected on
context cost; the tiering keeps the baseline small while the triggers pull in
the rest when relevant.

## Consequences

- Load-on-demand docs depend on the agent reading them when triggered, a weaker
  guarantee than an import. To hedge, the single safety-critical GitHub rule
  (approval before external actions) is stated inline, not deferred.
- The trigger table itself stays in always-on context, so it costs a few lines
  regardless - an acceptable price for the routing.
- On-demand references must resolve from the consumer's working directory (see
  [ADR 003](003-absolute-import-paths.md)).

> Always-on membership has since changed: `style` was removed
> ([013](013-style-rules-in-tooling-not-context.md)), `git` moved on-demand
> ([019](019-git-on-demand-via-skills.md)), and `workflow` was folded
> directly into `CLAUDE.md` ([020](020-fold-workflow-into-claude-md.md)). The
> two-tier decision here is unchanged.
