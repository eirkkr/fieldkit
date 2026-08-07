# Decisions

Lightweight architecture decision records (ADRs) for non-obvious design choices.
See [conventions/decisions.md](../../conventions/decisions.md) for the format.

| #   | Decision                                                                                                  | Status     |
| --- | --------------------------------------------------------------------------------------------------------- | ---------- |
| 001 | [Distribute conventions by @-import](001-import-not-copy.md)                                              | Accepted   |
| 002 | [Tier always-on vs load-on-demand](002-always-on-vs-load-on-demand.md)                                    | Accepted   |
| 003 | [Absolute paths in CLAUDE.md](003-absolute-import-paths.md)                                               | Superseded |
| 004 | [Lint with uvx, not a uv project](004-lint-via-uvx.md)                                                    | Accepted   |
| 005 | [Flat, content-shaped structure](005-flat-repo-structure.md)                                              | Accepted   |
| 006 | [Symlink kit reference](006-symlink-kit-reference.md)                                                     | Accepted   |
| 007 | [Agents don't run linters](007-agents-dont-run-linters.md)                                                | Accepted   |
| 008 | [Gate on outward or irreversible actions](008-outward-irreversible.md)                                    | Accepted   |
| 009 | [User-level commands, per-repo conventions](009-user-level-commands-not-conventions.md)                   | Superseded |
| 010 | [Python hub and on-demand spokes](010-python-hub-and-spokes.md)                                           | Accepted   |
| 011 | [WIP on branches; gate PR creation](011-wip-on-branches.md)                                               | Accepted   |
| 012 | [Per-consumer reconcile marker](012-reconcile-marker.md)                                                  | Accepted   |
| 013 | [Style rules in tooling, not LLM context](013-style-rules-in-tooling-not-context.md)                      | Accepted   |
| 014 | [Skills, not slash commands](014-skills-not-commands.md)                                                  | Accepted   |
| 015 | [Delegate mechanical, ungated git steps only](015-mechanical-subagent-boundary.md)                        | Superseded |
| 016 | [Pair a thin skill with a worker agent](016-skill-agent-pair.md)                                          | Accepted   |
| 017 | [Disable AI attribution via settings, not instructions](017-attribution-via-settings-not-instructions.md) | Accepted   |
| 018 | [Rely on venv activation, not an inline uv run rule](018-venv-activation-not-uv-run.md)                   | Accepted   |
| 019 | [Route git actions through skills; git.md on demand](019-git-on-demand-via-skills.md)                     | Accepted   |
| 020 | [Fold workflow.md into CLAUDE.md](020-fold-workflow-into-claude-md.md)                                    | Accepted   |
| 021 | [Adopt OpenSpec, centralised via the kit](021-adopt-openspec-centralised-via-kit.md)                      | Superseded |
| 022 | [Make OpenSpec skills model-discoverable](022-openspec-skills-model-discoverable.md)                      | Accepted   |
| 023 | [Block default-branch commits with a git hook](023-block-default-branch-commits-via-hook.md)              | Accepted   |
| 024 | [Fix and catch formatter drift in one Stop hook](024-stop-hook-for-formatter-drift.md)                    | Accepted   |
| 025 | [State skill routing and push cadence always-on](025-skill-routing-stated-always-on.md)                   | Accepted   |
| 026 | [Keep PR descriptions in sync, gated on approval](026-pr-description-sync-on-push.md)                     | Accepted   |
| 027 | [Move push's judgment calls to the caller](027-push-decisions-move-to-caller.md)                          | Accepted   |
| 028 | [Make opening a PR act-then-show, not gated](028-ungate-pr-creation.md)                                   | Accepted   |
| 029 | [Make PR title/body edits act-then-show too](029-ungate-pr-body-edits.md)                                 | Accepted   |
| 030 | [Ungate merging; caller drafts the squash message](030-ungate-merge.md)                                   | Accepted   |
| 031 | [Re-gate PR/merge invocation, unless directly invoked](031-regate-pr-and-merge-invocation.md)              | Accepted   |
