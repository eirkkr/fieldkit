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

## Specifying to decide, not only to build

A change is usually written because the work is going to happen. It is
also a legitimate way to find out **whether it should** - and that use
needs saying, because nothing else in this file implies it.

Writing the design is the cheapest instrument available for costing work
that sounds obviously worthwhile. A proposal argues from what a change
offers; a build plan is forced to say what every part of it costs, and
the two can disagree badly. Where a decision is large, reversible only
once, and argued mostly from principle, drafting the change before
committing to it is worth the days it takes.

**Watch the plan's growth as a signal, not just as an estimate
correction.** A plan that stops growing has been understood. One still
growing at the end of its own audit has not, and that is information
about whether to proceed rather than about how long it will take. Track
the task count across revisions: growth with no scope added means the
work is larger than anyone can currently see, and the rate of discovery
matters more than the total. Discovery that tapers is a plan converging;
discovery that is still turning up defects on the last pass is not.

**If the answer turns out to be no, the design is the most valuable
thing produced and it has nowhere obvious to go.** The archive is for
completed changes and syncs deltas into the living specs, which is
exactly wrong here - it would assert the work shipped and leave specs
describing behaviour that does not exist somewhere a later sync could
reach. Move it to a directory that says what it is, outside the specs
tooling's reach, and link it from the ADR recording the decision. Keep
it in the tense it was written in; rewriting it to fit the outcome edits
the evidence. What a later reader wants from it is the rejected
alternatives, which are the expensive part of the thinking, and the task
plan, which is the cost argument in a form no ADR can carry.

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
- When a change replaces a component - a library, a datastore, a
  framework - the risk is rarely in the features being replaced. Those
  are visible, and get ported. It is in the **guarantees the old one
  supplied incidentally**, which nothing wrote down because nothing had
  to provide them. Audit for these explicitly: they are invisible in any
  comparison of what each option *offers*, because they were never
  anyone's feature.

  Worked example, from a consumer repo's evaluation of moving off a
  document store. Three surfaced, none of them in the ADR that compared
  the two databases: API keys could not outlive their user because they
  were embedded in the user's document; a background thread could safely
  share the request's connection because the driver's client was
  thread-safe; and records written before a mid-file fault stayed
  written, because each record's write stood alone. Each would have
  shipped broken. The prompt that finds them is "what does the current
  design rely on that no line of code asks for?".

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
  complete from the user's point of view or unreachable. Three ways to get
  there, cheapest first:
  - **Not wired up.** The code is built and tested, but nothing reaches it -
    a route not registered, a command not added to its group, a function with
    no caller yet. Costs nothing and needs no cleanup.
  - **Behind a flag.** Off by default, switched on by a later stage. For work
    that has to be reachable to be exercised end to end. The flag belongs to
    the change, and removing it is a task in the stage that finishes the work
    - not a knob that outlives it.
  - **Beside the old path.** Build the replacement alongside what exists and
    swap in one stage, rather than half-migrating in each.

  Walking-skeleton ordering tends to produce the first on its own, and
  ordering stages so it does is cheaper than reaching for a flag: a stage
  that needs one is often a boundary drawn in the wrong place.
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
- **The stage's diff is the PR.** Because the PR holds exactly one stage,
  the note links `/pull/<n>/files` - no range to assemble, no base commit to
  carry - with `git diff <default-branch>...HEAD` beside it for the terminal.
  The PR view leads because it alone holds state: files tick off as they are
  read, a file a later fix touches again un-ticks itself, comments outlive
  the session. Under it, one line per task - number, subject, commit URL,
  which renders that commit against its parent. Those are a walking aid, not
  a second review surface, so the reviewer takes the stage whole or task by
  task as it deserves.
- **Two bookmarks, both in the note.** `Reviewed at` ends every note, marked
  awaiting approval until the gate closes, then filled with the commit
  approved before the box is ticked - so a stage sent back and fixed records
  the tree after the fixes. It is the record of what was signed off, since
  the squash discards the branch holding it; it is not a base, as the next
  stage starts from the merge commit. `Change based at <commit>` is recorded
  by the first stage and carried forward unchanged: the default branch's tip
  when the change began, which only the final review needs and nothing else
  remembers once the stages have merged separately.
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
  is for, even when most of it is already in. The final stage then merges
  like any other, and the archive - moving the change folder, syncing its
  delta into the living specs - follows in a small PR of its own.

A gate sent back is fixed inside its own stage, not carried into the next
one - and inside its own PR, which has not merged yet.
