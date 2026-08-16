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
  and `tasks.md` (implementation steps) - the sections below map the
  durable guidance from the old manual flow onto these three.

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
- Progress lives in `tasks.md`'s own checkboxes, ticked as
  `openspec-apply-change` (or you, by hand) completes each task; `openspec
  status` reads them back. No separate progress doc to keep in sync.

## Review (the `review-gated` schema)

Review runs at three scopes ([ADR 034](../docs/decisions/034-review-gated-openspec-schema.md)).
Only the second and third involve a human.

- **Per task.** The implementer checks the work against that task's own
  `Done when ...` condition before ticking the box. A box whose condition
  could not be verified stays unticked.
- **Per stage.** Every stage's last task is a `REVIEW GATE`, and it is a
  full stop: the gate is not ticked and the next stage does not start until
  a human approves. The stage is green before the gate is reached - nobody
  is asked to sign off on a broken tree. The review note is written into
  `tasks.md` under the gate, so it outlives the session and archives with
  the change. It covers what changed since the previous gate, any departure
  from the plan, how to verify (exact commands, plus manual steps), what to
  look at closely, and what is deliberately not done yet.
- **The stage's diff, written out.** Each note opens with both ways of
  reading the stage under review: `git diff <base>..HEAD` for a terminal, and
  the remote's `<forge>/compare/<base>...<branch>` view for a browser. Spelt
  out in full, so the reviewer copies or clicks rather than assembling them.
  The far end is left open - `HEAD`, the branch - so both stay right while
  the review runs and fixes land.
- **The gate's bookmark.** That base is the previous gate's commit, and it is
  recorded because nothing else knows it. Every review note ends with a
  `Reviewed at` heading, marked awaiting approval while the stage is under
  review; approving the gate fills it with the commit approved and ticks the
  box, in that order - so a stage sent back and fixed records the commit
  after the fixes, not the one first presented. A change's first gate has no
  predecessor, so its base is `git merge-base <default-branch> HEAD`, the
  whole branch so far - the commit, not the branch name, which moves and
  would shift the diff underneath the note. The bookmark holds only while the
  branch's history does: rewriting an approved commit strands the SHA in
  abandoned history, where it still resolves and still diffs, silently
  against the wrong base.
- **Per change.** The last stage of every change is the final review: the
  built code against the change's own proposal, design and delta specs, in
  both directions - unmet requirements, and things built that nothing asked
  for. The artifacts are corrected to describe what was actually built
  (durable decisions become ADRs), the diff is hand-walked for the
  conventions CI cannot see, and then it iterates with the human until they
  are satisfied. A change is not complete, and is not archived, before that.

A gate sent back is fixed inside its own stage, not carried into the next
one.
