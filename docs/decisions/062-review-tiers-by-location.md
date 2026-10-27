# 062 - Review tiers are set by where code lives

## Decision

Each path in a consumer repo is assigned one of three review tiers, in a zone map kept in the repo. A diff is classified by the paths it touches, with no commit history, no step tags, and no judgement from the agent that wrote it.

| Tier | Reviewed by | Typical contents |
| --- | --- | --- |
| `person` | A person, every line | Interfaces and types, domain rules, test cases, migrations, auth and secrets, CI and hooks, LLM prompts, the zone map itself |
| `agent` | A fresh agent, plus tests | Implementation where tests miss some failures: logging, error handling, performance |
| `machine` | Automated checks only, run locally or in CI | Generated code, mechanical code, and implementation behind a contract the tests cover |

A consumer declares the paths that skip a person in an optional `docs/review-zones.md`: a table with one row per glob, giving its tier and why the paths may have it. A web app might hold:

```markdown
| Paths | Tier | Why a person need not read it |
| --- | --- | --- |
| `templates/**` | agent | Presentation only: the rules a page renders live in `person` files, and the PR's Try it shows the result |
| `static/**/*.js` | agent | Display and wiring in the browser: no rule a person must agree to is decided here |
| `**/*.gen.*` | machine | Generated from a reviewed schema, and the check regenerates and diffs it |
| `src/**/mapping.py` | machine | Mechanical by lint: complexity is capped at 1 |
| `tests/**/factories.py` | agent | Builds test data: what a test asserts lives in the test cases, which stay `person` |
```

- A path no row matches is `person`. A repo without the file keeps today's review of every line, and `person` rows are never needed.
- Where globs overlap, the higher tier wins: `person` over `agent` over `machine`.
- The zone map itself, and the test cases - the files the test runner collects, such as `test_*.py` - are `person` whatever a row says. The zone script refuses a row that would lower either. Test support code - fixtures, factories, setup and teardown, test-data builders - may be declared `agent`.
- Every row needs its reason, given in terms of the rule the paths escape, as [records.md](../../conventions/records.md) asks of any exemption list. A reason that only describes the files ("static assets") can't be used to refuse the next row, and the list grows by precedent. The zone script refuses a row with no reason.

Test cases are in the `person` tier on purpose. The `machine` tier is only safe if a person has agreed to what the tests check: a behaviour change needs a change to a test case, and a test case is read, so an agent cannot change behaviour without a person seeing it. A diff that touches only `machine`-tier code and no test cases is a refactor the existing tests already vouch for.

Test support code is different. A broken fixture or factory usually makes tests fail loudly rather than pass wrongly, so an agent's review is enough. The same rule holds as for mechanical code: a helper that hides an assertion, such as `assert_order_valid()`, is a test case, and lives with them.

The two lower tiers are reached differently. A repo may declare a path `agent` with a reason alone: a fresh agent still reads every line, so nothing further guards it. That suits static files and templates, which need no restructuring to qualify. The `machine` tier needs a mechanical guard as well, since nothing reads it. Each kind of `machine`-tier file has its own guard, and a file that fails its guard moves up to `agent`:

| Kind | Example | Guard |
| --- | --- | --- |
| Generated | A client built from an OpenAPI spec, ORM models, protobuf stubs | The check regenerates the code and fails on any difference. A person reviews the source it is built from |
| Lint-capped | Mappers, DTOs, route registration, CLI wiring, pass-through adapters | A lint scoped to these files caps complexity at 1, so they hold no branches |
| Test-held | Implementation behind a contract the tests cover | A scheduled mutation run per zone. Surviving mutants demote the area to `agent` |

Mechanical code goes in its own files, because a glob cannot see inside a file: one that mixes a rule with its plumbing has to be `person`, and the plumbing gets read too. One directory per concept, with fixed suffixes, keeps the parts side by side:

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

A decision never goes in a mechanical file. If a mapper needs a condition, the condition belongs in the rules file, and the lint enforces that. Each repo picks its own suffixes; the kit requires only that every tier can be matched by glob.

Every stage keeps its human gate. The zone map changes what the gate asks a person to read, not whether the gate exists (see "Gates", under Reason).

## Reason

A stage's gate asks a person to weigh every line of an agent's diff equally. Most of a typical diff is plumbing that tests already hold, so the decisions get the same skim as the mapper beside them. Separating what a person must read from what tests can hold puts the reviewer's attention where it is needed.

Tests can only check code against something a person has agreed to. So the line falls between the specification - contracts, tests, decisions, and code no test can vouch for - and the implementation of it. That line is mostly a property of where code lives: a migration needs reading whoever writes it, and a generated client never does.

Rejected:

- **Tagging each stage step `Read` or `Tests`.** Steps map to commits, so the tags would give a reading list per commit. But the agent classifies its own work, the tags live in history rather than in the code, and every stage re-decides the same question for the same files.
- **CODEOWNERS alone.** GitHub's CODEOWNERS file can say only "needs this owner" or nothing. It enforces the `person` tier natively, so `person` globs are mirrored into it with "Require review from Code Owners" on, but it has no way to tell `agent` from `machine`.
- **A tier per file, recorded by comment in the file.** It can't be matched by glob, and nothing stops a change to the file from changing its own tier unread.
- **A section in each repo's `CLAUDE.md`.** It would load in every session to serve one script, against the budget [060](060-budget-the-always-loaded-context.md) sets. A dedicated file at a fixed path, as `docs/version-pins.md` is for [044](044-repo-pins-in-a-consumer-file.md), gives the script a path that a renamed heading can't break.
- **A bare glob list with no reasons, as CODEOWNERS is.** Nothing would record why a path was let off a person's review, so nothing could be used to refuse the next path.

### Gates

A stage whose diff touches only the `machine` tier could merge on green CI, with no human gate. That is the largest gain on offer, and the largest change: it amends [041](041-stage-is-the-merge-unit.md) and [049](049-approval-does-not-start-the-next-stage.md). The options:

| Option | A `machine`-only stage | Gain | Cost |
| --- | --- | --- | --- |
| A. Keep every gate | Stops as now; the PR body says nothing needs reading | Faster reviews, no rule change | The reviewer still has to say yes |
| B. Auto-merge `machine`-only stages | Merges on green CI; the reviewer is told afterwards | Stages run unattended between real decisions | Amends two ADRs; a mis-zoned file merges unread |
| C. Opt in per repo | B where a repo's map says so, A elsewhere | Repos with strong guards get the gain | Two behaviours to document and test |

A is proposed first. It delivers most of the value, and it produces evidence of how often the map is right. That evidence, not an argument from principle, is what would justify B or C later.

## Consequences

- **The kit's part is small:** a convention, a zone script and three CI recipes. The changes it implies:
  - `conventions/specs.md`: the PR body gains **Read these** (the `person` files touched, and why) and **Held by checks** (the `machine` files touched, and the guard each passed), both computed from the map. An `agent`-tier file touched means the fresh-agent review runs by default, not on offer.
  - `change-stage`: runs the zone script before opening the PR and pastes its output into the body.
  - `change-plan`: the plan review flags a requirement whose implementation would sit in a `machine` file, a sign the rule is in the wrong place.
  - `conventions/ci.md`: the three guards.
  - A consumer's `docs/review-zones.md`: optional, and without it every path is `person`.
- **Most of the cost falls on consumer repos,** which restructure toward the layout. That can be gradual: a file not yet split stays `person`. Declaring templates and static files `agent` needs no restructuring, so a repo gets a first benefit from a row or two.
- **Risks, and what holds each:**
  - A file is zoned wrongly and a rule lands unread. The map is itself `person`, and every row carries its reason, so each zoning choice is reviewed. The guards demote `machine` files that stop qualifying.
  - A rule creeps into a mechanical file. The complexity lint fails the build.
  - Tests cover lines but not behaviour, so test-held code looks safe. The mutation run demotes the area.
  - Spreading a concept across files hurts navigation. One directory per concept with fixed suffixes keeps it together.
  - Harm no test sees, such as a secret logged from a mapper. Secret handling and logging configuration are `person`, and a security review is offered when they are touched.
  - Mutation runs are slow. They run on a schedule per zone, not per PR.
- **This repo gains less.** The kit has no tests, so the `machine` tier is out of reach here, and only declared `agent` rows apply, such as templates. The full benefit is in consumer repos with test suites, and one of those is where the zone script should be tried first.
- **Rollout, if accepted,** as a change of four stages:
    1. The convention: tiers, the zone map format and the file-structure rule. Nothing enforced yet.
    2. The guards: regenerate-and-diff, the scoped complexity lint, the scheduled mutation run.
    3. The zone script, which reads `docs/review-zones.md` and refuses rows that break its rules, and the PR body sections.
    4. Gates, only if B or C is chosen: amend 041 and 049, and teach `merge` to merge a `machine`-only stage on green CI.
- **Open questions** before this is accepted:
  - Gates: A, B or C?
  - Are three tiers right, or is `agent` versus `machine` a line a repo won't maintain?
  - Is the mutation run required for test-held files, or only advised?
  - May a repo declare a path `machine` with a reason alone, skipping agent review too, for files such as static assets that hold no logic at all?
