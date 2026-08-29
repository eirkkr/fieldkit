# 041 - Make the stage the unit of merge, not just of review

## Decision

A stage is what gets merged. Each stage of a review-gated change is its own
branch off the default branch and its own PR, opened when the stage reaches
its gate and merged when that gate closes. The change folder stays the unit
of planning and spans several PRs.

Three consequences follow, and are decided here together because each is
load-bearing for the others:

- **One commit per task.** The task is the unit of commit, with the task
  number in the subject, so the reviewer can walk a stage commit by commit
  or read it as one diff.
- **The gate note gains per-task links.** Beside the stage diff it already
  carries, the note lists each task's commit URL, which renders that
  commit's diff against its parent.
- **The draft PR is retired.** [034](034-review-gated-openspec-schema.md)
  opened one draft PR per change at its first gate, held draft across every
  stage, and marked it ready at the final review. With one PR per stage
  there is nothing for the draft state to mean.

The final stage keeps its whole-change review, but reviews merged work: its
whole-change diff is a comparison against the default branch, not a PR view.
Archiving the change is its own last PR.

This amends [034](034-review-gated-openspec-schema.md).

## Reason

034 fixed review granularity and left merge granularity alone. Gates land
every 3-6 tasks, but the change merges once, so the reviewer reads in
instalments while the tree receives one large drop. Everything 034 argues
about catching a decision "at the moment it is still cheap to reverse" stops
at the merge boundary: a stage approved at the first gate does not reach the
default branch until the last one closes, by which time later stages are
built on it anyway.

The measured shape in a consumer repo, after 034 was adopted: proposal PRs of
774 to 1476 lines, then implementation PRs of 1195, 1607 and 3168 lines, and
one change of 8359 lines across 92 files. The stages inside those changes
were correctly sized - 3-6 tasks, each ending green, several of them plainly
mergeable on their own (a predicate with its tests and nothing calling it; a
module moved with no behaviour change). They simply had nowhere to go. The
unit of work that was already right was never the unit that shipped.

**Per-task gating was considered and rejected.** It is the obvious next
increment and it does not work. A task deliberately does not leave the tree
green - the schema's own rule is that a *stage* is the smallest group that
does - so a per-task gate asks a human to sign off on knowingly incomplete
work: one task adds a predicate, the next adds its tests. Making that
reviewable needs each task to narrate what is broken and which later task
repairs it, which is precisely the information the stage boundary exists to
encode; a task needing a paragraph to explain its incompleteness is evidence
the stage was the right boundary. Review cost is also not proportional to
diff size - there is a fixed cost per review event, reloading context and
working out what is being looked at - and at a task's tens of lines that
fixed cost dominates. Worst, it re-opens one level down the exact split this
ADR closes: a task cannot be a merge unit for the same reason it cannot be a
gate, so review and merge would part company again.

**Per-task commits get most of that benefit at no interrupt cost.** A commit
URL renders that commit against its parent, needs no PR, and works on any
pushed commit, so the walking aid the per-task proposal wanted costs nothing
but a commit discipline the kit already recommends. The two views divide by
what they are for: the stage diff stays the PR file view because it alone
holds review state - files tick off as they are read, a re-touched file
un-ticks itself, comments outlive the session - while per-task links are
walking aids where state would be meaningless. Squash-merge discards those
commits, but they are alive during the review, which is when they are wanted.

**The draft state was a workaround for the long-lived PR.** It meant "stages
still to come", which is why 034 needed it: a PR open across a whole change
had to say it was asking nothing of anyone yet. A stage PR opens when its
stage is ready to be reviewed, so it is simply ready. Retiring it removes a
concept rather than adding one, and removes with it the pressure on CI
configuration: workflows triggered on `pull_request` alone do not run while
no PR is open, so a stage's mid-work pushes are silent and CI first sees the
branch at the gate, against a tree that is already green.

**Suppressing CI on drafts was considered and rejected.** It was raised as a
way to keep intermediate task commits from reporting red. It restores exactly
the failure that made 034's arrangement awkward - CI first seeing the branch
once the work is finished - and contradicts the rule that green means the
PR's checks rather than the tests alone, which exists because linting is
deferred to CI and work deferred to CI is work nobody looked at. Under
one-PR-per-stage the problem it solves does not arise.

Alternatives rejected:

- **Stacked PRs**, one per stage based on the previous. Keeps a change
  abandonable as a unit and reviewable in instalments, but every stage's
  branch is then based on something still under review, which
  [git.md](../../conventions/git.md) rules out as an anti-pattern, and it
  needs external tooling to restack after a gate sends a stage back.
- **Keeping one PR and merging more often.** Not available: one PR is one
  merge. Merging more often means more PRs.
- **Syncing delta specs into the living specs per stage**, so
  `openspec/specs/` tracks what is actually on the default branch. Rejected
  as churn for no reader: the change folder is the in-flight record, and a
  half-synced capability spec describes a state nobody is asked to rely on.

## Consequences

- **A stage must now be independently mergeable, not merely green.** This is
  a stronger constraint than 034's, and the main new cost of authoring. Work
  half-built when the stage ends must be unreachable rather than merely
  untested, or else complete from the user's point of view. The conventions
  name three ways to get there - not wired up, behind a flag, or built beside
  the old path - in that order of preference, since the first costs nothing
  and the others leave something to remove. Walking-skeleton ordering mostly
  produces the first already; it is now a rule rather than a tendency.
- **A bad stage is fixed forward.** Abandoning a change used to cost a
  branch. Approved stages are now on the default branch, so a change
  abandoned late leaves merged work behind that has to be reverted
  deliberately. This is the real trade, and it is the one accepted.
- **More PRs, more CI runs, more merge events per change.** A five-stage
  change is five PRs plus the archive PR, where it was one.
- **The `Reviewed at` bookmark stops being load-bearing.** A stage's diff is
  now its whole PR, so no gate needs a base commit to subtract the previous
  stage, and 034's stranded-SHA hazard - a rebase silently moving an approved
  commit into abandoned history, where it still resolves and still diffs -
  largely dissolves with it. The heading stays as the record of which tree
  was signed off, since the squash-merge discards the branch that held it,
  and a gate sent back and fixed still bookmarks the tree after the fixes.
- **One bookmark is genuinely needed, and it is new.** The final review reads
  the whole change, which is by then spread across separately merged PRs, so
  the first stage's note records `Change based at <commit>` - the default
  branch's tip when the change began - and every later note carries it
  forward. Nothing else remembers it.
- **The PR-opening exemption widens.** KIT.md exempted the single draft PR a
  review-gated change opens; that becomes one PR per stage. Without the
  widening, the change trades large reviews for repeated approval prompts.
  Merging stays gated exactly as before - approval plus green CI - so a
  stage does not merge itself.
- **The living specs lag further behind the code.** Stages are on the
  default branch while `openspec/specs/` still describes the pre-change
  behaviour, until archive. Accepted above; worth knowing when reading a
  spec while a change is in flight.
- **Adopting repos with a CI workaround for the long-lived draft can drop
  it.** A workflow that opted drafts in, or a job that opted them out, was
  tuned for a PR that sat in draft across a whole change. Neither is needed
  once stage PRs are short-lived and never draft.
