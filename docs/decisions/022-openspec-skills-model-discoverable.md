# 022 - Make OpenSpec skills model-discoverable

## Decision

Drop `disable-model-invocation: true` from the vendored `openspec-*` skills
in `repo-skills/`. `just openspec-refresh` no longer patches it back in when
regenerating from upstream. In a repo that has opted in (`openspec/` exists,
skills linked via `enable-openspec.sh`), Claude can now suggest and invoke
these skills on its own, same as any other skill description in context.

## Reason

ADR 021 hid the OpenSpec skills from idle context per-session, accepting
that "Claude won't proactively suggest the workflow" because the commands
were meant to be as deliberate as `/push` and `/pr`. In practice that trade
was too conservative: proposing or continuing a change is exactly the kind
of moment a fresh agent should recognise on its own ("there's an open
`openspec/changes/` folder relevant to this ask") rather than requiring the
user to remember and type the right `/openspec-*` command.

Per-repo opt-in (the rest of ADR 021) already bounds the context cost: only
a repo that ran `enable-openspec.sh` carries these skill descriptions at
all, and only while `openspec/` exists. That's the same scoping `/push` and
`/pr` don't get (they're user-level, always in context), so the two cases
aren't as analogous as ADR 021 treated them.

## Consequences

- Repos with OpenSpec enabled now carry the six `openspec-*` skill
  descriptions in idle context every session, not just when explicitly
  invoked. Accepted: it's already opt-in per repo, and the set is small.
- `scripts/openspec-refresh.sh` is simpler: it no longer patches generated
  SKILL.md files before vendoring them.
- `conventions/specs.md` updated to describe auto-discovery instead of
  deliberate `/` invocation.
- This does not revisit the rest of ADR 021 (centralisation via the kit,
  per-repo opt-in, vendoring mechanism) - only the per-session hiding.
