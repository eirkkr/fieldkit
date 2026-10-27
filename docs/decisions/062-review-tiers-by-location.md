# 062 - Review tiers are set by where code lives

## Decision

Each path in a consumer repo is assigned one of three review tiers, in a zone map kept in the repo. A diff is classified by the paths it touches, with no commit history, no step tags, and no judgement from the agent that wrote it.

| Tier | Reviewed by | Typical contents |
| --- | --- | --- |
| `person` | A person, every line | Interfaces and types, domain rules, test cases, migrations, auth and secrets, CI and hooks, LLM prompts, the zone map itself |
| `agent` | A fresh agent, every line, plus the tests | Orchestration, error handling, templates, static files, test support code |
| `machine` | Automated checks only, run locally or in CI | Generated code, mechanical code, implementation behind a contract the tests cover, and assets that aren't code |

A *fresh* agent is one given the files and the rules they are checked against, and nothing from the planning or the build, as `conventions/specs.md` defines it.

### The zone map

A consumer declares its tiers in an optional `docs/review-zones.md`. It names the repo's test cases on its first line, then holds a table with one row per glob, giving its tier, the guard that keeps a `machine` row honest, and why the paths may have it. A web app might hold:

```markdown
Test cases: `tests/**/test_*.py`

| Paths | Tier | Guard | Why |
| --- | --- | --- | --- |
| `templates/**` | agent | - | Presentation only: the rules a page renders live in `person` files |
| `templates/auth/**` | person | - | Renders the sign-in and reset flows, where a wrong field leaks an account |
| `static/**/*.js` | agent | - | Display and wiring in the browser: no rule a person must agree to is decided here |
| `static/img/**` | machine | - | Not code: a review of an image diff can catch nothing |
| `**/*.gen.*` | machine | `gen-check` | Generated from a reviewed schema |
| `src/**/mapping.py` | machine | `lint-mechanical` | Mechanical: complexity is capped at 1 |
| `tests/**/factories.py` | agent | - | Builds test data: what a test asserts lives in the test cases |
```

- A path no row matches is `person`, so a repo without the file keeps today's review of every line. A `person` row carves a path back out of a broader row.
- Where globs overlap, the higher tier wins: `person` over `agent` over `machine`.
- The zone map itself, and the test cases its first line names, are `person` whatever a row says. Test support code - fixtures, factories, setup and teardown - may be declared `agent`.
- Every row needs its reason, given in terms of the rule the paths escape, as [records.md](../../conventions/records.md) asks of any exemption list. A reason that only describes the files ("static assets") can't be used to refuse the next row, and the list grows by precedent.

The *zone script* reads the map and a diff, and reports the files the diff touches in each tier. It refuses a map with a row that has no reason, or that would lower the map or the test cases. A `machine` row's guard is the name of a `just` recipe in the repo, as `just check` is relied on by name ([044](044-repo-pins-in-a-consumer-file.md)): the kit can't know how each repo regenerates its code or which linter it runs. The script refuses a `machine` row whose recipe doesn't exist, unless the row is for files that aren't code, and runs the recipe of every `machine` row the diff touches.

### What each tier needs

**`person`** needs nothing: it is where every path starts. Test cases are kept here on purpose. The `machine` tier is only safe if a person has agreed to what the tests check, and a behaviour change needs a change to a test case, so an agent cannot change behaviour without a person seeing it.

**`agent`** needs a reason, and the fresh-agent review. That review runs on every diff that touches an `agent` file, not only when the reviewer asks for one. This is an exception to `conventions/specs.md`, where review is offered and runs on request: the tier's whole claim is that an agent reads every line, and a review that may not run would leave those files read by nobody. Templates, static code and test support code qualify with no restructuring. The review also checks that test support code holds no assertions: a helper that hides one, such as `assert_order_valid()`, is a test case, and belongs with them.

**`machine`** needs a reason and a mechanical guard, since nothing reads it. Each kind has its own guard:

| Kind | Example | Guard |
| --- | --- | --- |
| Generated | A client built from an OpenAPI spec, ORM models, protobuf stubs | The check regenerates the code and fails on any difference. A person reviews the source it is built from |
| Lint-capped | Mappers, DTOs, route registration, CLI wiring, pass-through adapters | A lint scoped to these files caps complexity at 1, so they hold no branches |
| Test-held | Implementation behind a contract the tests cover | A mutation run on a schedule, which every repo with test-held rows must have |
| Not code | Images, fonts, vendored files the repo didn't write | None: the reason alone, since reading them could catch nothing |

The reason-only route is for files that aren't code. Code the repo wrote never reaches `machine` without a guard.

**When a guard fails, nothing changes tier by itself.** The regenerate-and-diff check and the lint fail the build. Someone then either fixes the file - moving the `if` out of the mapper into a rules file - or edits the zone map to raise the file's tier. The map is `person`, so that edit is read. The mutation run is too slow for every PR, so it doesn't fail one. When it finds tests that miss injected bugs in a row's paths, it reports which row, and proposes raising that row to `agent` for a person to accept.

### Code structure

Mechanical code goes in its own files, because a glob cannot see inside a file. A file that mixes a rule with its plumbing has to be `person`, and the plumbing gets read too. One directory per concept, with fixed suffixes, keeps the parts side by side:

```text
orders/
  types.py        # person: the contract
  rules.py        # person: the decisions
  service.py      # agent: orchestration, error handling
  mapping.py      # machine: lint-capped, no branches
  client.gen.py   # machine: regenerated and diffed
tests/orders/
  test_rules.py   # person: the test cases
  factories.py    # agent: test data, no assertions
```

A decision never goes in a `machine` file: if a mapper needs a condition, the condition belongs in the rules file. Each repo picks its own suffixes; the kit requires only that every tier can be matched by glob.

### At the gate

Every stage keeps its human gate (see "Gates", under Reason). The PR body names the `person` files touched, which is what the reviewer reads. The `agent` files are covered by the review that runs on them, and the `machine` files by their guards. The reviewer may open any of them, but isn't asked to.

### Wiring it into a consumer

The kit's existing pattern for consumer wiring carries it: an idempotent `enable-*.sh` script, a reusable workflow the consumer's CI calls, and `/kit-reconcile` re-running every enable script a repo has run.

- **`.fieldkit/scripts/enable-review-zones.sh`** writes a starter `docs/review-zones.md` holding only the `Test cases:` line, and a caller workflow for the kit's reusable one, as `enable-pr-checks.sh` does. With no rows every path is `person`, so enabling changes nothing until a row is added.
- **The reusable workflow** checks out the consumer at the PR's commit and the kit beside it, then runs the zone script on the PR's diff: the map's rules, the tiers touched, and the guard of every `machine` row touched.
- **Locally**, `change-stage` runs the same script from `.fieldkit/scripts/` before it opens a PR.
- **For Python repos**, the kit ships the `lint-mechanical` recipe's configuration: ruff's complexity rule at 1, scoped to the mechanical files. Other languages write their own recipe.

The kit itself is not a consumer - it has no `.fieldkit` link to itself - so it runs the script from `just lint`, against its own map.

### Adopting it

A repo adopts in steps, cheapest first. Each is worth having on its own, and a repo can stop after any of them.

1. **Enable it.** The map has no rows and nothing changes, which proves the wiring.
2. **Rows that need no refactoring.** Images, fonts and vendored files to `machine`; templates, static code and test support code to `agent`. A row and a reason each.
3. **Generated code.** Where the repo already generates code, a `gen-check` recipe and a row.
4. **Refactoring toward the layout.** Real work, so planned as a change, one concept per stage: split the mechanical code out of mixed files, add the scoped lint, add the row.
5. **Test-held rows,** only once a mutation tool runs on a schedule with a baseline score. They are the riskiest rows, so they come after the cheaper tiers have shown the map can be trusted.

## Reason

A stage's gate asks a person to weigh every line of an agent's diff equally. Most of a typical diff is plumbing that tests already hold, so the decisions get the same skim as the mapper beside them. Separating what a person must read from what tests can hold puts the reviewer's attention where it is needed.

Tests can only check code against something a person has agreed to. So the line falls between the specification - contracts, test cases, decisions, and code no test can vouch for - and the implementation of it. That line is mostly a property of where code lives: a migration needs reading whoever writes it, and a generated client never does.

Rejected:

- **Tagging each stage step `Read` or `Tests`.** Steps map to commits, so the tags would give a reading list per commit. But the agent classifies its own work, the tags live in history rather than in the code, and every stage re-decides the same question for the same files.
- **CODEOWNERS alone.** GitHub's CODEOWNERS file can say only "needs this owner" or nothing. It can enforce the `person` tier - an owner on `*`, then each `agent` and `machine` glob listed with no owner - but it can't tell `agent` from `machine`, and it records no reasons. Requiring owner review would also block a repo whose PRs are opened under its owner's own account, since GitHub doesn't let an author approve their own PR.
- **A tier per file, recorded by comment in the file.** It can't be matched by glob, and nothing stops a change to the file from changing its own tier unread.
- **A section in each repo's `CLAUDE.md`.** It would load in every session to serve one script, the reason [044](044-repo-pins-in-a-consumer-file.md) gave for keeping pins out of `CLAUDE.md`. A dedicated file at a fixed path, as `docs/version-pins.md` is there, gives the script a path that a renamed heading can't break.
- **Inferring test cases from the test runner's collection rules.** Every runner collects differently, and the script would have to know each one. A glob on the map's first line is one line for the repo to write, and the script reads it the same way whatever the runner.
- **Moving a file up a tier automatically when its guard fails.** Files would change tier without anyone deciding it, and a regression would merge with a changed tier rather than a red build.
- **The mutation run as advised, not required.** It is the only guard on test-held files. Optional, it would leave them in `machine` with nothing checking them.

### Gates

A stage whose diff touches only the `machine` tier could merge on green CI, with no human gate. That is the largest gain on offer, and the largest change. The stage as the unit of merge comes from [041](041-stage-is-the-merge-unit.md) and the gate from [049](049-approval-does-not-start-the-next-stage.md), both now stated in `conventions/specs.md` and the `change-stage` skill under [054](054-a-change-is-an-issue.md). Merging is also an ask-first action in `KIT.md`'s approval table, and the `merge` skill assumes approval was given. The options:

| Option | A `machine`-only stage | Gain | Cost |
| --- | --- | --- | --- |
| A. Keep every gate | Stops as now; the PR body says nothing needs reading | Faster reviews, no rule change | The reviewer still has to say yes |
| B. Merge `machine`-only stages on green CI | Merges; the reviewer is told afterwards | Stages run unattended between real decisions | Changes specs.md, `change-stage`, `KIT.md`'s merge row and `merge`; a mis-zoned file merges unread |
| C. Opt in per repo | B where a repo's map says so, A elsewhere | Repos with strong guards get the gain | Two behaviours to document and test |

A is chosen. It delivers most of the value, and it produces evidence of how often the map is right. That evidence, not an argument from principle, is what would justify B or C later. The condition for revisiting is a record of `machine`-only PRs the reviewer approved unread and nothing later found wrong in. A single repo's convenience is not one.

## Consequences

- **The kit's part is small:** a convention, the zone script and three check recipes. The changes it implies:
  - `conventions/specs.md`: the PR body gains **Read these**, the `person` files touched, computed by the zone script. The fresh-agent review runs on every diff that touches an `agent` file, as the exception above.
  - `change-stage`: runs the zone script before opening the PR, puts **Read these** in the body, and runs the agent review where `agent` files are touched.
  - `conventions/ci.md`: the guards - regenerate-and-diff, the scoped complexity lint, the scheduled mutation run.
  - A consumer's `docs/review-zones.md`: optional, and without it every path is `person`.
- **Most of the cost falls on consumer repos,** which restructure toward the layout. That can be gradual: a file not yet split stays `person`. Rows for templates, static files and test support code need no restructuring, so a repo gets a first benefit from a row or two.
- **Risks, and what holds each:**
  - A file is zoned wrongly and a rule lands unread. The map is `person`, and every row carries its reason, so each zoning choice is read.
  - A rule creeps into a mechanical file. A branch fails the lint. A decision written as data - a lookup table, a constant - passes it, so a row's reason should say why its files hold none; tables and constants that decide something belong in rules files.
  - A lint-capped file changes behaviour with no branch, such as a mapper swapping two fields. Only the tests can catch it, so lint-capped files are worth a test through the contract they serve.
  - Tests cover lines but not behaviour, so test-held code looks safe. The mutation run proposes raising the row.
  - Spreading a concept across files hurts navigation. One directory per concept with fixed suffixes keeps it together.
  - A secret leaks from a file nobody reads, such as a value logged from a mapper. Code that handles secrets is `person`.
- **This repo gains little, but is the first to run it.** The kit has no tests, and its conventions, skills, hooks and scripts are instructions or logic, so they stay `person`. Its map is small: `repo-skills/` to `machine`, vendored and regenerated by `just openspec-refresh`, with `check-overlays` failing when an overlay and its vendored skill disagree; `package-lock.json` to `machine`, generated by npm; `LICENSE` and `NOTICE` as files that aren't code. That is enough to exercise the script and the map's rules on a real repo. The full benefit is in consumer repos with test suites.
- **The rules above belong in a convention doc,** not an ADR: [decisions.md](../../conventions/decisions.md) keeps the rule a reader must follow out of the record of why. They are here while this is proposed, and stage 1 moves them.
- **Rollout** as a change of four stages:
    1. The convention: tiers, the zone map format and the file-structure rule, moved out of this ADR, and the kit's own map. Nothing enforced yet.
    2. The zone script and its reusable workflow, the enable script, and the script in the kit's `just lint`.
    3. **Read these** in the PR body, and the agent review on `agent` files: `conventions/specs.md` and `change-stage`.
    4. The guards' recipes: the Python `lint-mechanical` configuration, and `conventions/ci.md` on regenerate-and-diff and the scheduled mutation run.

  A skill that surveys a repo and proposes rows, with the files that are mostly plumbing as refactoring targets, is not yet specified: it waits until stage 2 has run on a real consumer.
- **Open questions** before this is accepted:
  - Are three tiers right, or is `agent` versus `machine` a line a repo won't maintain?
