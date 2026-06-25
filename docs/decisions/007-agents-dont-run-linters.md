# 007 - Agents don't run linters or formatters

## Decision

Agents don't run formatters or linters, and don't gate their work on a clean
lint/format pass, unless explicitly asked. They match the surrounding style by
hand and rely on ordinary care while writing; the human and CI own the
machine-enforced pass. The rule lives in `conventions/workflow.md`.

## Reason

Agents iterating on lint and format output is a major source of token churn:
run the tool, parse the output, fix, re-run, repeat - often over purely
cosmetic findings a formatter would rewrite anyway. The human is happy to run
these tools and CI already enforces them, so the agent's involvement is
redundant cost.

Alternatives rejected:

- **Agent runs lint and fixes only genuine defects.** Incoherent: the agent can
  only know what the linter found by running it and reading the output, which is
  the churn we're removing. Correctness defects (undefined name, unused import)
  are caught by reading one's own code while writing, not by a lint pass.
- **A silent auto-format hook.** Hooks live in `.claude/settings.json`, which
  doesn't travel through the `@.fieldkit` import, so it can't be a shared
  cross-repo rule; the command is also toolchain-specific per repo. Viable as a
  per-repo opt-in later, but not the generic mechanism. A hook that reports lint
  failures back to the agent would worsen churn, not fix it.

## Consequences

- A style slip or stray defect can reach CI. Accepted: it's cheaper to catch
  there once than to have the agent police it every session.
- Consumer-repo rules like "lint must pass before push/merge" are read as CI's
  and the human's gate, not one the agent drives. The workflow rule states this
  so the two don't conflict.
- Scope is linters and formatters only. Tests are deliberately excluded: their
  output is correctness feedback that improves the code, so iterating on tests
  is part of the agent's loop, not churn. The same lean-output discipline
  applies - run them concise (quiet, short traceback, fail-fast) to keep the
  loop cheap.
- If a repo wants formatting fully automated off the agent's plate, the path is
  a per-repo silent auto-format hook, documented as opt-in - not a change to
  this decision. Prefer firing it on stop (turn end) over per-edit: a formatter
  reorders whitespace, so per-edit reformatting can leave a later edit's
  `old_string` no longer matching the file, costing a failed edit and a re-read.
  On-stop timing lets the agent work against stable state.
- Guard that hook on a dirty working tree (`git status --porcelain | grep -q
  .`), not on a list of fixable file extensions. Skipping no-op turns (those
  that changed nothing) is worth the cheap `git status`, but enumerating
  extensions couples the guard to the format command: add a fixer for a new
  file type and the guard silently stops triggering for it. Running the
  formatter on a turn that touched only non-fixable files is a near-instant
  no-op; a newly added fixer that never fires is a silent drift bug. The coarse
  guard removes the coupling, so the hook stays correct as the format command
  grows.
