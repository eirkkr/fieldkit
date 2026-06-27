# 012 - Track reconcile state with a per-consumer marker

## Decision

Each consumer repo commits a `.fieldkit-rev` file at its root recording the kit
commit it was last reconciled to - a high-water mark. Its first
whitespace-delimited token is the SHA; a trailing `# <date> <subject>` comment is
for humans. `/kit-reconcile` reads it to default its range to `<marker>..HEAD`
and advances it on every run, opening a marker-only PR when the audit changes
nothing.

The command resolves its range from one optional argument: none uses the marker
(or, if the file is absent, the latest commit plus a warning); a number `N` uses
`HEAD~N..HEAD`; `latest` uses the latest commit only. The previous arbitrary
git-range argument is dropped.

`/kit-reconcile` reconciles *instructions* only. Codebase conformance is a
separate concern: the command surfaces which changed conventions have code
implications and offers to file issues; the actual sweep is deferred to a
future `/kit-audit` command, tracked by its own issue.

## Reason

The marker solves "I forget what commit we've reconciled up to" - it turns the
range into something computed, not remembered. It lives in the consumer because
the kit's own history cannot know each consumer's state, and it is committed -
unlike the gitignored `.fieldkit` symlink ([ADR 006](006-symlink-kit-reference.md))
- so it travels to every clone, collaborator, and CI checkout. Plain text so the
bump diffs visibly in the reconcile PR. It must be stored, not derived: a
consumer's git history records nothing about the kit's SHA.

Dropping the arbitrary range: `N` and `latest` are HEAD-anchored special cases
that cover every realistic need, and the marker handles the everyday path. An
arbitrary non-HEAD window is exotic and not worth the surface area; keeping every
mode HEAD-anchored is simpler to document.

The marker must advance even on a no-op reconcile, or it never catches up and
re-reviews clean commits forever. A marker-only PR - not a bare commit on `main`
- keeps this within the never-commit-to-main convention, and the trivial PR is
the audit trail.

Splitting instructions from codebase: most kit changes (workflow, git, PR
process) have zero code impact, so welding a repo-wide source sweep onto every
reconcile is wasteful and carries a wildly different blast radius and review
model. The marker tracks instruction-reconcile state; pending code work is
tracked by filed issues, mirroring workflow.md's "fix inline, else file an issue"
rule.

Alternatives rejected:

- **One command doing docs and code.** Forces a heavyweight, repo-wide sweep on
  changes that mostly need none, and merges two very different blast radii.
- **A second marker (`.fieldkit-code-rev`) for code state.** Over-engineered for
  a personal kit; filed issues carry the pending-code signal adequately.
- **Keeping the arbitrary git-range argument.** Redundant once `N`, `latest`, and
  the marker exist; its only unique capability is the exotic non-HEAD window.
- **A marker-only commit straight to `main` on a no-op.** Violates the
  never-commit-to-main / always-PR convention.

## Consequences

- Each consumer gains a committed `.fieldkit-rev`. The first `/kit-reconcile` on
  a repo without one reviews the latest commit, warns, and creates the file; the
  README setup documents it.
- The marker can drift from actual code conformance: it means "instructions
  reconciled to X," not "code conforms to X." Filed issues carry the code debt.
- `/kit-audit` is yet to be built, so until then the code-sweep half is manual;
  an issue tracks creating it.
- Builds on ADR 006: same per-consumer model, but committed rather than
  gitignored, since the marker must travel with the repo.
