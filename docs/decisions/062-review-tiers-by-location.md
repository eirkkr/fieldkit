# 062 - Review tiers are set by where code lives

## Decision

Each path in a consumer repo is assigned one of three review tiers, in a zone map kept in the repo. A diff is classified by the paths it touches, with no commit history, no step tags, and no judgement from the agent that wrote it.

| Tier | Reviewed by | Typical contents |
| --- | --- | --- |
| `person` | A person, every line | Interfaces and types, domain rules, tests, migrations, auth and secrets, CI and hooks, LLM prompts, the zone map itself |
| `agent` | A fresh agent, plus tests | Implementation where tests miss some failures: logging, error handling, performance |
| `tests` | CI only | Generated code, mechanical code, and implementation behind a contract the tests cover |

The map is a file at the repo root in CODEOWNERS-style globs, for example:

```text
# review-zones
person  src/**/types.py  src/**/rules.py  tests/**  migrations/**  .github/**
agent   src/**/service.py  src/**/adapters/**
tests   **/*.gen.*  src/**/mapping.py  src/**/wiring.py
```

Tests are in the `person` tier on purpose. A behaviour change needs a test change, and a test change is read, so an agent cannot change behaviour without a person seeing it. A diff that touches only `tests`-tier code and no tests is a refactor the existing tests already vouch for.

A file stays below `person` only while a mechanical guard says it may. Each kind of `tests`-tier file has its own guard, and a file that fails its guard moves up a tier:

| Kind | Example | Guard |
| --- | --- | --- |
| Generated | A client built from an OpenAPI spec, ORM models, protobuf stubs | CI regenerates the code and fails on any difference. A person reviews the source it is built from |
| Lint-capped | Mappers, DTOs, route registration, CLI wiring, pass-through adapters | A lint scoped to these files caps complexity at 1, so they hold no branches |
| Test-held | Implementation behind a contract the tests cover | A scheduled mutation run per zone. Surviving mutants demote the area to `agent` |

Mechanical code goes in its own files, because a glob cannot see inside a file: one that mixes a rule with its plumbing has to be `person`, and the plumbing gets read too. One directory per concept, with fixed suffixes, keeps the parts side by side:

```text
orders/
  types.py        # person: the contract
  rules.py        # person: the decisions
  test_rules.py   # person: what the rules must do
  service.py      # agent: orchestration, error handling
  mapping.py      # tests: lint-capped, no branches
  client.gen.py   # tests: regenerated and diffed in CI
```

A decision never goes in a mechanical file. If a mapper needs a condition, the condition belongs in the rules file, and the lint enforces that. Each repo picks its own suffixes; the kit requires only that every tier can be matched by glob.

Every stage keeps its human gate. The zone map changes what the gate asks a person to read, not whether the gate exists (see "Gates", under Reason).

## Reason

A stage's gate asks a person to weigh every line of an agent's diff equally. Most of a typical diff is plumbing that tests already hold, so the decisions get the same skim as the mapper beside them. Separating what a person must read from what tests can hold puts the reviewer's attention where it is needed.

Tests can only check code against something a person has agreed to. So the line falls between the specification - contracts, tests, decisions, and code no test can vouch for - and the implementation of it. That line is mostly a property of where code lives: a migration needs reading whoever writes it, and a generated client never does.

Rejected:

- **Tagging each stage step `Read` or `Tests`.** Steps map to commits, so the tags would give a reading list per commit. But the agent classifies its own work, the tags live in history rather than in the code, and every stage re-decides the same question for the same files.
- **CODEOWNERS alone.** GitHub's CODEOWNERS file can say only "needs this owner" or nothing. It enforces the `person` tier natively, so `person` globs are mirrored into it with "Require review from Code Owners" on, but it has no way to tell `agent` from `tests`.
- **A tier per file, recorded by comment in the file.** It can't be matched by glob, and nothing stops a change to the file from changing its own tier unread.

### Gates

A stage whose diff touches only the `tests` tier could merge on green CI, with no human gate. That is the largest gain on offer, and the largest change: it amends [041](041-stage-is-the-merge-unit.md) and [049](049-approval-does-not-start-the-next-stage.md). The options:

| Option | A `tests`-only stage | Gain | Cost |
| --- | --- | --- | --- |
| A. Keep every gate | Stops as now; the PR body says nothing needs reading | Faster reviews, no rule change | The reviewer still has to say yes |
| B. Auto-merge `tests`-only stages | Merges on green CI; the reviewer is told afterwards | Stages run unattended between real decisions | Amends two ADRs; a mis-zoned file merges unread |
| C. Opt in per repo | B where a repo's map says so, A elsewhere | Repos with strong guards get the gain | Two behaviours to document and test |

A is proposed first. It delivers most of the value, and it produces evidence of how often the map is right. That evidence, not an argument from principle, is what would justify B or C later.

## Consequences

- **The kit's part is small:** a convention, a zone script and three CI recipes. The changes it implies:
    - `conventions/specs.md`: the PR body gains **Read these** (the `person` files touched, and why) and **Held by tests** (the `tests` files touched, and the guard each passed), both computed from the map. An `agent`-tier file touched means the fresh-agent review runs by default, not on offer.
    - `change-stage`: runs the zone script before opening the PR and pastes its output into the body.
    - `change-plan`: the plan review flags a requirement whose implementation would sit in a `tests` file, a sign the rule is in the wrong place.
    - `conventions/ci.md`: the three guards.
    - A consumer's `CLAUDE.md`: `## Reviews` points to the zone map.
- **Most of the cost falls on consumer repos,** which restructure toward the layout. That can be gradual: a file not yet split stays `person`.
- **Risks, and what holds each:**
    - A file is zoned wrongly and a rule lands unread. The map is itself `person`, so each zoning choice is reviewed, and the guards demote files that stop qualifying.
    - A rule creeps into a mechanical file. The complexity lint fails the build.
    - Tests cover lines but not behaviour, so test-held code looks safe. The mutation run demotes the area.
    - Spreading a concept across files hurts navigation. One directory per concept with fixed suffixes keeps it together.
    - Harm no test sees, such as a secret logged from a mapper. Secret handling and logging configuration are `person`, and a security review is offered when they are touched.
    - Mutation runs are slow. They run on a schedule per zone, not per PR.
- **This repo gains little.** The kit has no tests, so nearly everything here would be `person`. The benefit is in consumer repos with test suites, and one of those is where the zone script should be tried first.
- **Rollout, if accepted,** as a change of four stages:
    1. The convention: tiers, the zone map format and the file-structure rule. Nothing enforced yet.
    2. The guards: regenerate-and-diff, the scoped complexity lint, the scheduled mutation run.
    3. The zone script and the PR body sections.
    4. Gates, only if B or C is chosen: amend 041 and 049, and teach `merge` to merge a `tests`-only stage on green CI.
- **Open questions** before this is accepted:
    - Gates: A, B or C?
    - Are three tiers right, or is `agent` versus `tests` a line a repo won't maintain?
    - Is the mutation run required for test-held files, or only advised?
    - Does the zone map get its own file, or a section in each repo's `CLAUDE.md`?
