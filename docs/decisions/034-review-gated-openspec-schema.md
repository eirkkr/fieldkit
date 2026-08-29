# 034 - Gate OpenSpec stages on human review

## Decision

Replace the stock `spec-driven` OpenSpec workflow with a kit-owned
`review-gated` schema that makes human review the spine of a change rather
than something that happens once at the end.

Three levels of review, by scope:

- **L1, per task.** The agent checks its own work against that task's
  written `Done when ...` condition before ticking the box, and does not
  tick a box it could not verify. No human involved.
- **L2, per stage.** Every stage's last task is a `REVIEW GATE`: a hard
  stop. The agent never ticks it and never starts the next stage. It writes
  a review note into `tasks.md` under the gate - the stage's own diff as a
  PR file-view link and a `git diff` command, what changed since the last
  gate,
  departures from the plan, how to verify, what to look at closely, what is
  deliberately not done yet, and a `Reviewed at` heading awaiting approval -
  then waits. Approval fills that heading with the commit approved, which is
  the base the next gate's diff runs from, and only then is the box ticked.
- **L3, per change.** Every change ends with a final-review stage that
  checks the built code against the change's own proposal, design and delta
  specs in both directions, reconciles the artifacts with what was actually
  built, and then iterates with the human until they are satisfied.

Tasks are sized to one action with one checkable done-condition, naming the
files they touch. Stages are sized to the smallest group that leaves the tree
green and expresses one idea - 3-6 tasks, 8 at most - with the guidance
biased toward splitting.

Mechanically:

- The schema lives in the kit at `schemas/review-gated/`, not in each repo.
  `enable-openspec.sh` creates `openspec/schemas/review-gated/` as a real
  directory and symlinks the files inside it, then sets `schema:
  review-gated` in the repo's `openspec/config.yaml`.
- The rules are stated in the schema's `tasks` instruction (how to author
  gates) and its `apply` instruction (how to honour them). Both reach the
  agent through `openspec instructions`.
- A new `repo-skills-overlay/` holds markdown appended to vendored skills
  after `just openspec-refresh` rsyncs them, patching the gate rules into
  `openspec-apply-change` and an archive block into
  `openspec-archive-change`.

## Reason

The stock schema asks for tasks "small enough to complete in one session"
and otherwise leaves granularity open, and its apply loop is explicitly
told to "keep going through tasks until done or blocked". Those combine
into the failure this change exists to prevent: the agent runs the entire
change end to end and presents one large diff, at the point where the human
has the least context and the most sunk cost. Review then either rubber-
stamps or restarts.

Gating at the stage boundary puts the human in at the moment a decision is
still cheap to reverse, and bounds what any one review has to hold in the
head. Everything else follows from making that review cheap: the tasks are
bite-sized so a gate lands often, a stage must end green so the reviewer is
never asked to judge a half-wired tree, and the note is written into
`tasks.md` rather than only spoken, so it survives the session, and archives
with the change as the record of what was reviewed and when.

The stage's diff is written into the note because "what changed since the
last gate" is only useful if the reviewer can get to it: assembling it means
knowing where the last gate ended, which is what they came to the note to
find out. The PR's file view leads because it alone holds state - files tick
off as they are read, a file a later stage touches again un-ticks itself,
comments survive the session the way the note does - with a `git diff`
command beside it for the terminal. A compare link was carried as a third
until the file view proved to subsume it; it now appears only where there is
no PR. Both end at the literal `HEAD`, which the file view resolves to the
PR's tip, so neither goes stale when a stage is sent back and fixes land.

A change's first gate opens that PR as a draft rather than asking first: a PR
before the first gate has nothing to show, so opening it is part of reaching
the gate. The draft state is what makes it ungated - no review is requested
and nothing merges, while CI reports on the stage independently of the
agent's claim that it is green. The final stage marks it ready, the draft
having meant "stages still to come".

`Reviewed at` supplies the base. Recording it at approval rather than at
writing is what makes it true: a stage sent back and fixed bookmarks the
commit after the fixes, the tree actually approved. It is a commit, not a
branch name, which moves and would change an earlier stage's diff long after
it was reviewed - and because a range needs both ends inside the PR, a first
gate, whose base predates it, links the plain file view instead.

"What to look at closely" and "not done yet" are in the note for asymmetric
reasons. The first is the line a confident-sounding summary omits, and it is
the one that actually directs attention. The second stops the reviewer
spending the gate reporting gaps that a later stage already covers.

L3 is separate from the last stage's L2 gate because they ask different
questions. A gate asks whether this stage is right; the final review asks
whether the change did what it set out to do, which is only answerable
once. It reconciles the artifacts before archive, so the delta specs
synced into `openspec/specs/` describe what was built rather than what was
planned.

The three levels are scope tiers rather than depth tiers (light/standard/
deep per stage, chosen by risk). Depth tiers were considered and rejected:
they ask the author to predict where review effort will pay off, which is
the prediction that is wrong precisely when it matters, and a stage tagged
"light" is an invitation to skim exactly the change that turns out to
matter. Uniform gates are more interruptions but no judgement calls, and
stage size is already the lever for cost.

Mechanism notes:

- **A kit-owned schema, not per-repo forks.** `openspec schema fork` copies
  into a repo, which would drift per adopting repo and re-run the ADR 021
  argument for centralisation. Linking is the same pull model as
  `repo-skills/`.
- **Files symlinked, not the schema directory.** Symlinking
  `openspec/schemas/review-gated` itself fails: OpenSpec enumerates schemas
  with a directory check that a symlink does not satisfy, and reports
  `Unknown schema 'review-gated'` while `openspec schema which` still
  resolves it. A real directory with symlinked contents works.
- **An overlay, not hand-edits.** `just openspec-refresh` does
  `rsync --delete` from a fresh `openspec init`, so anything written into
  `repo-skills/` is silently reverted at the next refresh. ADR 022 removed
  the kit's only patch, leaving no patch step to extend; this reintroduces
  one as an append-only overlay rather than a `.patch`, so an upstream
  rewording cannot fail to apply.
- **Belt and braces.** The gate rules are in the schema *and* in the skill
  overlay because the vendored skill's own "keep going until done"
  guardrail directly contradicts them, and an agent blowing through a gate
  defeats the entire change.

Alternatives rejected:

- **`openspec/config.yaml` `rules:` only.** Per-artifact rules are injected
  into instructions and need no fork, but they are per-repo (the drift
  problem again) and cannot touch `apply.instruction`, which is where the
  stop actually has to live.
- **Overlay only, no schema.** The skills are the orchestration, but
  `tasks.md` authoring is driven by the schema's instruction and template.
  Gates that the apply phase honours but no one writes are worthless.

## Consequences

- Changes take more round trips by construction. That is the point, but it
  makes stage sizing the main cost lever - an over-large change with
  ten stages will feel heavy, and the answer is a smaller change.
- A recorded `Reviewed at` commit is only as stable as the branch's history.
  Rewriting an approved commit - a rebase, an amend - strands the SHA in
  abandoned history, where it still resolves and still produces a diff,
  silently against the wrong base. Nothing detects this; a change in flight
  is a branch to add commits to, not to rewrite.
- Adopting repos must re-run `.fieldkit/scripts/enable-openspec.sh` to pick
  up the schema link and the `config.yaml` selection. Existing in-flight
  changes keep the schema named in their own `.openspec.yaml`; only new
  changes get gates.
- The linked files dangle in any checkout without a `.fieldkit` symlink, CI
  included - the same property the `.claude/skills` links already have, but
  now inside the linted tree, where a tool that walks every file fails on
  them with an IO error rather than ignoring them. Adopting repos must
  exclude `openspec/schemas` from any such tool; a Python consumer needed it
  for `ruff format`, which reads Markdown. Copying the schema in instead would
  avoid this, at the cost of the per-repo drift centralisation exists to
  prevent.
- Each adopting repo also needs a `per-file-ignores` entry of its own for
  the linked templates (see the README). `rumdl check` doesn't need it - it
  resolves the symlink and finds the kit's config - but rumdl's language
  server reads only the workspace-root config, so without it an editor
  flags `MD041` on files the repo doesn't own. The globs need a leading
  `**/` in both places: rumdl matches them against the path as passed, and
  a language server passes an absolute one.
- `repo-skills/` is no longer verbatim upstream. It is still generated, so
  it stays lint-excluded, but a diff against a stock `openspec init` will
  now show the overlay sections.
- The kit now carries a schema it must keep merged with upstream. A future
  `openspec-refresh` that changes the stock `spec-driven` schema will not
  touch `schemas/review-gated/`, so the proposal/specs/design instructions
  it inherited can go stale. They are copied verbatim today apart from one
  added paragraph each, which keeps that merge readable.

> Amended by [041](041-stage-is-the-merge-unit.md): the stage is now the unit
> of merge as well as of review - each stage is its own branch and PR, merged
> when its gate closes - so the single draft PR this ADR opens at a change's
> first gate is retired, and the per-change PR lifecycle described above no
> longer holds. The three review levels, the gate mechanics, and the
> `Reviewed at` bookmark are unchanged; 041 adds one commit per task and
> per-task links in the note.

