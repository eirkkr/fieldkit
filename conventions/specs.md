# Writing implementation specs

How to write a specification another contributor - or a fresh agent - can
implement without re-deriving your context. In a repo with an `openspec/`
directory (see ADR 021), OpenSpec carries the artifacts and lifecycle
described here; this file is the content guidance for what goes in them.

## Workflow

- OpenSpec has two layers: living specs in `openspec/specs/` (the current,
  agreed behaviour of each capability) and disposable change folders in
  `openspec/changes/<name>/` (a proposal in flight). A change is archived to
  `openspec/changes/archive/` on completion, syncing its delta into the
  living specs.
- The `openspec-*` skills are model-discoverable: Claude can invoke them on
  its own when a repo has `openspec/` activated, or you can invoke one
  directly from the `/` menu.
- A change's artifacts are `proposal.md` (what & why), `design.md` (how),
  and `tasks.md` (implementation steps); the sections below say what belongs
  in each.

## What a spec is

- A spec defines **contracts, decisions, and constraints** - not the
  artifacts that satisfy them (that is implementation). When unsure where
  something belongs, ask: is this a contract/decision, or the thing built to
  meet it?
- Record non-obvious or reversed decisions as ADRs (see `decisions.md`): the
  spec states the decision, the ADR holds the why and the rejected
  alternatives. Write the ADR when the decision settles - while drafting the
  change's artifacts, not as a deferred doc task - so the rationale does not
  accumulate in `proposal.md`/`design.md` and drift from the record.
- Flag provisional or placeholder content loudly, so a reader does not mistake
  a rough draft for a settled rule.

## Contracts (proposal.md, design.md)

- Pin the interface between modules/stages explicitly (fields, types, enums,
  nullability) in `design.md`. Prefer file-in/file-out boundaries so each
  part runs and is tested in isolation.
- An example artifact can be authoritative for *shape*, but its *values* must
  be audited before becoming a golden fixture - a golden test enshrines
  whatever is in it, bugs included.

## Build plan (tasks.md)

- Break work into ordered tasks, each with an explicit **definition-of-done**
  and, where one exists, a "copy/adapt this existing file" reference. Size the
  detail for the least-skilled likely implementer.
- One task is **one action with one done-condition**, naming the files it
  touches, written in about five lines or fewer. Split on "and": adding a
  dependency, configuring it, and proving it loads are three tasks. The
  exception is an atomic pair - a rename and its call sites - where the tree
  is broken in between.
- **Walking-skeleton first:** get the whole thing running end to end (fixtures
  or stubs for unbuilt parts) before deepening any one part; then change one
  thing at a time on a tested base. Build order is not feature order.
- Tasks are grouped into **stages**. A stage is the smallest group that
  leaves the tree green and says one thing - 3-6 tasks, 8 at the most. When
  the choice is open, split: a smaller stage is a cheaper review.
- A stage is also **independently mergeable**, because merging is what
  happens to it ([ADR 041](../docs/decisions/041-stage-is-the-merge-unit.md)).
  Green is not enough: anything half-built when the stage ends is either
  complete from the user's point of view or unreachable - a route not
  registered, a command not wired in, a flag off. Walking-skeleton ordering
  tends to produce this anyway; here it is a requirement, and it is what
  stage boundaries are chosen on when green alone would allow either.
- **One commit per task**, its subject naming the task number. The reviewer
  then chooses their own granularity at the gate - walk the stage commit by
  commit when it is fiddly, read it as one diff when it is not.
- Progress lives in `tasks.md`'s own checkboxes, ticked as
  `openspec-apply-change` (or you, by hand) completes each task; `openspec
  status` reads them back. No separate progress doc to keep in sync.

## Review (the `review-gated` schema)

Review runs at three scopes ([ADR 034](../docs/decisions/034-review-gated-openspec-schema.md)),
and the stage is the unit of merge as well as of review
([ADR 041](../docs/decisions/041-stage-is-the-merge-unit.md)). Only the
second and third scopes involve a human.

- **Per task.** The implementer checks the work against that task's own
  `Done when ...` condition before ticking the box, and commits it. A box
  whose condition could not be verified stays unticked.
- **Per stage.** Every stage's last task is a `REVIEW GATE`, and it is a
  full stop: the gate is not ticked and the next stage does not start until
  a human approves. The stage is green before the gate is reached - nobody
  is asked to sign off on a broken tree. The review note is written into
  `tasks.md` under the gate, so it outlives the session and archives with
  the change. It covers what changed since the previous gate, any departure
  from the plan, how to verify (exact commands, plus manual steps), what to
  look at closely, and what is deliberately not done yet.
- **One stage, one branch, one PR.** Each stage branches off the default
  branch, and the PR opens when the stage reaches its gate - the PR is the
  surface the note points at, so opening it is part of reaching the gate.
  Approving the gate merges it; the next stage branches off the result.
  There is no draft state to set: a stage PR exists only once it is ready to
  be read.
- **Green means the PR's checks, not the tests alone.** Linting is CI's
  pass rather than the agent's, so work deferred to it is work nobody
  looked at. Reaching a gate includes reading the PR's checks and
  recording their state in the note, and a stage's last verification task
  runs the repo's full check rather than its test command. A red check
  means the stage is not ready, and is fixed before a reviewer sees it.
  Workflows triggered on `pull_request` alone stay quiet until the PR opens,
  so CI first sees the branch at the gate, against a tree already green.
- **The stage's diff is the PR.** Because the PR holds exactly one stage,
  the note links `/pull/<n>/files` - no range to assemble, no base commit to
  carry - with `git diff <default-branch>...HEAD` beside it for the
  terminal. The PR view leads because it alone holds state: files tick off
  as they are read, a file a later fix touches again un-ticks itself,
  comments outlive the session.
- **Per-task links walk the stage.** Under the stage diff the note lists one
  line per task - its number, its subject, and its commit URL, which renders
  that commit against its parent. They are a walking aid, not a second
  review surface: the reviewer reads the stage whole or follows it task by
  task, whichever the stage deserves. Squash-merge discards the commits, but
  they are alive for the length of the review.
- **The gate's bookmark.** Every note ends with a `Reviewed at` heading,
  marked awaiting approval until the gate closes, then filled with the
  commit approved before the box is ticked - so a stage sent back and fixed
  records the tree after the fixes, not the one first presented. It is the
  record of what was signed off, kept because nothing else holds it once the
  PR is squashed; it is no longer load-bearing as a base, since the next
  stage starts from the merge commit.
- **The change's own base.** The first stage's note also records `Change
  based at <commit>` - the default branch's tip when the change began. The
  final review needs it, and nothing else remembers it once the stages have
  merged separately.
- **Per change.** The last stage of every change is the final review: the
  built code against the change's own proposal, design and delta specs, in
  three directions - unmet requirements, things built that nothing asked
  for, and requirements met only by construction, with no test behind them.
  The third is the one nothing else catches.
- **The final gate's order of work.** The diff is hand-walked for the
  conventions CI cannot see *before* the artifacts are corrected to what was
  actually built (durable decisions become ADRs) - the walk turns up
  artifact-shaped findings, so correcting first means correcting twice. Then
  every issue the change references, in artifacts, docstrings and the docs it
  touches, is re-read: still open, and still about the thing cited. Then the
  gate iterates with the human until they are satisfied. A change is not
  complete, and is not archived, before that.
- **The final note's two diffs.** The last stage's own diff leads, as any
  stage's does - its PR, its per-task links. The whole change follows, based
  at the `Change based at` commit recorded by the first stage: mostly already
  merged, so it is a `git diff <base>...<default-branch>` and a
  `git log --oneline <base>..<default-branch>` over the stages that landed,
  rather than a PR view. Signing off the change as a whole is what the gate
  is for, even when most of it is already in.
- **Archiving is its own PR.** The final stage merges like any other; the
  archive - moving the change folder and syncing its delta into the living
  specs - follows in a small PR of its own, once the reviewer is satisfied.

A gate sent back is fixed inside its own stage, not carried into the next
one - and inside its own PR, which has not merged yet.
