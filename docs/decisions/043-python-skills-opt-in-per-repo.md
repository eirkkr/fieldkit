# 043 - Ship Python-only skills per-repo, from `python-skills/`

## Decision

Skills that only apply in a Python repo live in `python-skills/`.
`.fieldkit/scripts/enable-python.sh`, run from a consumer's root, symlinks
each into that repo's `.claude/skills/`; `just install` does not link them.

`update-deps` is the first, moved in from a Python consumer that grew it
locally. It keeps its name, so existing `/update-deps` references still
resolve. It runs inline, with no paired agent.

## Reason

[ADR 009](009-user-level-commands-not-conventions.md) and
[014](014-skills-not-commands.md) put pull-style assets user-level because an
uninvoked skill costs nothing. That fails for a uv-only skill: its description
loads in every session on the machine, and invites a run where `uv tree`
doesn't exist. [022](022-openspec-skills-model-discoverable.md) already
accepted per-repo opt-in as the bound on a skill set's context cost.

Not `repo-skills/`, because that is generated: `just openspec-refresh`
rsyncs it with `--delete`, which would remove a hand-written skill.

A language-named script, because the opt-in unit is the language: a Python
repo should get every Python skill, including later ones. Rerunning the
script links new skills and prunes removed ones.

No agent pair ([ADR 016](016-skill-agent-pair.md)): the work is changelog
judgment with the human confirming each bump, not a mechanical step.

Alternatives rejected:

- **User-level under `skills/`.** The context cost above.
- **Leave it in the consumer.** Other Python consumers would re-derive it,
  and it already leans on kit conventions it can only track from outside.
- **Link it from `enable-openspec.sh`.** OpenSpec and Python are independent
  opt-ins.

## Consequences

- ADR 014 gains a foot note limiting "future pull-style assets go user-level"
  to skills that apply in every repo.
- The README and `conventions/python/README.md` describe the directory,
  script, and skill.
- `skills/kit-reconcile` needs no change: its wiring check already reruns
  `enable-*.sh` for dangling `.claude/skills` links.
- The committed links dangle in any checkout without `.fieldkit`, CI
  included - as the OpenSpec links do.
- A second language would follow the same `<language>-skills/` and
  `enable-<language>.sh` pattern; nothing is generalised ahead of one.
