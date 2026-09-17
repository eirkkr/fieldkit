# 043 - Ship Python-only skills per-repo, from `python-skills/`

## Decision

Skills that only make sense in a Python repo live in a top-level
`python-skills/` directory and reach a consumer through a per-repo opt-in:
`.fieldkit/scripts/enable-python.sh`, run from the consumer's root, symlinks
each `python-skills/<name>/` into that repo's `.claude/skills/`. `just
install` does not link them user-level.

`update-deps` is the first instance - a dependency review and bump procedure
for uv projects, moved into the kit from a Python consumer that had grown it
locally. It keeps its name, so a consumer's existing references to
`/update-deps` resolve unchanged once the link replaces the local copy.

The skill runs inline, with no paired agent.

## Reason

[ADR 009](009-user-level-commands-not-conventions.md) and
[014](014-skills-not-commands.md) send pull-style assets user-level, on the
grounds that an uninvoked skill costs nothing. That held for `push` and `pr`,
which apply in every repo. It doesn't hold for a skill whose description is
meaningful only in a uv project: the description sits in context in every
session on the machine - non-Python repos, repos with no kit at all - and
invites a model-invoked run where `uv tree` doesn't exist. That is the
containment argument 009 made for conventions, and
[022](022-openspec-skills-model-discoverable.md) already accepted
per-repo opt-in as the bound on a skill set's context cost.

A separate directory, rather than adding to `repo-skills/`, because
`repo-skills/` is generated: `just openspec-refresh` rsyncs it with
`--delete` from the `openspec` CLI, which would remove a hand-written skill,
and `.rumdl.toml` excludes it from linting on the same grounds. Keeping
authored and vendored skills apart keeps that rule simple.

A language-named script and directory rather than a general "enable these
skills" linker, because the opt-in unit is the language: a repo becomes
Python once and should get the whole set, including skills added later -
rerunning the script picks those up, and prunes links to ones removed.

No agent pair ([ADR 016](016-skill-agent-pair.md)): the work is changelog
reading and adoption judgment with the human in the loop at each bump, not
the mechanical, ungated step that justifies an isolated worker.

Alternatives rejected:

- **User-level under `skills/`.** Rejected for the context cost above.
- **Leave the skill in the consumer.** Every other Python consumer would
  re-derive it, and the copy that exists already cites kit conventions
  (`conventions/python/setup.md`) that it can only track from outside.
- **Link it from `enable-openspec.sh` or a combined enable script.** OpenSpec
  and Python are independent opt-ins; a repo can take either.

## Consequences

- The README's Layout and Setup sections describe `python-skills/` and the
  script; `conventions/python/README.md` points at the skill from its
  dependency row.
- `skills/kit-reconcile` needs no change: its wiring check already finds
  dangling `.claude/skills` links and reruns the matching `enable-*.sh`.
- The consumer the skill came from replaces its local directory with the
  link, and moves its repo-specific pins out of the skill body - see
  [ADR 044](044-repo-pins-in-a-consumer-file.md).
- Like the OpenSpec links, the committed links dangle in any checkout with
  no `.fieldkit` symlink, CI included.
- A second language would get its own `<language>-skills/` and
  `enable-<language>.sh` on the same pattern; nothing here generalises in
  advance of one.
