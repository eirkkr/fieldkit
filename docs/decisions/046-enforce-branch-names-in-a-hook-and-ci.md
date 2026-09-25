# 046 - Enforce branch names in a PreToolUse hook and CI

## Decision

`conventions/git.md` gains a hard limit on branch names: at most 50
characters, prefix included.

The kit ships `hooks/pretooluse-branch-name.py`, a Claude Code `PreToolUse`
hook on `Bash`. It refuses a command that creates or renames a branch to a
name without one of the prefixes `git.md` allows, or over that limit, through
the documented JSON `deny` decision, with a reason saying which rule the name
breaks and pointing at `git.md`.

- **Commands caught:** `git checkout -b|-B`, `git switch -c|-C|--create|
  --force-create`, `git branch <name>` (creation), `git branch -m|-M|-c|-C
  [<old>] <new>` (the new name), and `git worktree add -b|-B`. The command is
  tokenised with `shlex` and each simple command in a compound one is checked,
  with `cd <dir>` and `git -C <dir>` followed to find the repo it acts on.
- **Fails open.** Anything not read with confidence is let through:
  unparseable shell, a name containing `$`, a backtick or a backslash, a `git
  branch` flag outside the creating and renaming sets, and `git worktree add
  <path>` without `-b`. The registered command ends `|| true`, so a crash is
  inert too.
- **Where it applies.** Only in a repo that reaches the kit: one with a
  `.fieldkit` entry at the root of its working tree or of its main worktree,
  or the kit itself. Everywhere else it lets everything through.
- **The rules live in the hook.** `PREFIXES` and `MAX_LENGTH` are constants
  at the top of `pretooluse-branch-name.py`, with a comment marking them as a
  mirror of `git.md`'s Branches bullets. Nothing checks the two agree.
- **`EnterWorktree` is left out.** Its input carries a worktree `name`, not a
  branch name; the branch Claude Code derives from it is not in the tool's
  schema.
- **CI backs it for everyone.** `just check-branch-name` runs the hook's
  `--name` mode on the PR's branch in CI, or the checked-out branch locally.
  CI reaches it through `.github/workflows/branch-name.yml`, a reusable
  workflow that checks out the kit and runs the recipe there. Consumers call
  it at the kit's `main`, from a caller workflow that
  `scripts/enable-branch-check.sh` writes; it also triggers on the kit's own
  PRs, at the PR's commit, so the consumer path is tested before it reaches
  consumers. That is the kit's only CI check of the
  name - it stays out of `just lint`, which `lint.yml` runs, so a bad name
  fails once. `just check` runs both locally. PRs opened by a bot are skipped.
- **Registration.** `scripts/register_stop_hook.py` becomes
  `scripts/register_hooks.py` (and its shell wrapper `register-hooks.sh`),
  registering both kit hooks from one table, with the in-place rewrite of a
  moved or renamed entry kept per hook.

## Reason

Branch naming is enforced only as prose in `git.md`, which is on the
load-on-demand list for "a git action `push`/`pr`/`merge` don't cover".
Creating a branch is such an action but too small to feel like one, so the
read keeps not happening: a session in this repo branched as `public-release`,
and one in a consumer repo as `package-structure-design`, both caught by the
human rather than by anything structural.

A `PreToolUse` hook fires at the moment of branching, before anything is on
the branch, and its refusal reaches Claude as a reason it can act on in the
same turn - a rename costs one retry, not a rewrite of pushed history.

A `pre-commit` check was proposed for the same rule first. It fires at the
first commit and catches everyone, but it was stuck on refuse-or-warn: it
cannot tell an agent from a human, and refusing gets in the way of a human's
scratch branch. Splitting enforcement removes the dilemma - this hook refuses
Claude at branching, and CI checks everyone at the PR, which scratch branches
never reach - so the `pre-commit` check is not built.

Why the choices above:

- **Failing open** over refusing when unsure: a missed catch is no worse than
  having no hook, while a false refusal blocks legitimate work, possibly in a
  way Claude can't route around without help.
- **Scoping to kit repos:** registration is machine-wide, but the naming rule
  is the kit's, not a universal one. Imposing it on an unrelated repo - a
  third-party checkout, a repo with its own naming scheme - would be a false
  refusal by definition. The main worktree is checked as well as the current
  one because `.fieldkit` is gitignored, so a linked worktree never has it.
- **Constants in the hook** over the alternatives. The hook is the only
  reader of the rules - CI, and any later `pre-commit` check, call its
  `--name` mode rather than reading them themselves - so a shared data file
  (JSON, TOML) would be a second file with one reader. Parsing them out of
  `git.md`'s prose, tried first, kept one copy but made the bullets' exact
  wording load-bearing: a rewording that stopped a bullet
  parsing silently switched that check off, and a lint check existed only to
  catch it.
- **No check that `git.md` and the constants agree.** A mismatch surfaces by
  itself: every refusal states the rules from the code and points at
  `git.md`, so the first person to hit one sees both. The two change in one
  PR, and doc accuracy is audited in review. A drift check would buy early
  warning on a list that rarely changes, at the cost of matching prose.
- **A hard length limit** over guidance to keep names short: a number in
  the doc can be checked, where "a few words" can't, and the likeliest
  source of a long name is an agent turning an issue title into one. No
  standard sets one - the Conventional Branch spec asks only for a concise
  description, and GitHub's UI truncates by available width, not at a fixed
  count - so the number is a house rule, like the commit subject's limit
  in `git.md`. 50 matches that limit's target, and fits practice: none of
  this repo's 78 branch names so far exceeds it (longest 41), nor any of one
  consumer repo's 208 (longest 48), so it refuses the outlier without
  renaming anything that exists.
- **Characters, not words:** characters are what truncation depends on, and a
  word cap still admits five long words.
- **Prefix and length only**, not lowercase or hyphenation: both are closed
  and mechanical, the style rules are looser and more likely to refuse a name
  a human would accept.
- **CI as well as the hook:** the hook sees only Claude, and only through
  Bash; CI sees every PR's branch, however it was made. It also answers the
  objection that made the `pre-commit` check's refuse-or-warn question hard:
  refusing gets in the way of scratch branches, spikes and bisect runs - none
  of which become PRs, so CI never sees them.
- **A reusable workflow reading the kit's `main`** over a script copied into
  each consumer: the rules stay in one place and a change reaches every
  consumer at once. A consumer can't pin the rules this way - the same trade
  the `.fieldkit` symlink already makes for the conventions themselves.
- **Bots exempt:** a bot's branch names come from its own config, which the
  rules can't instruct. Failing its PRs would only be noise.
- **One registration script** over a second copy of the Stop one: the two
  would differ only in event, matcher and file name, and the legacy-rename
  handling from ADR 035 would otherwise be duplicated.

Alternatives rejected:

- **The `pre-commit` check, alone or alongside.** Fires after work has piled
  up on the wrongly named branch, cannot tell an agent from a human, and
  needs installing per clone; the hook and CI between them cover what it
  would.
- **A non-zero exit to refuse.** Indistinguishable from a crash, which must
  fail open; the JSON decision is the documented block.
- **Guessing `EnterWorktree`'s branch name.** It would hard-code an
  undocumented naming scheme that can change under the hook, and a name
  Claude doesn't choose directly isn't the failure being fixed.

## Consequences

- Claude's branch creation through Bash in a kit repo is refused on the spot;
  every other branch - a human's, or one `EnterWorktree` made - is caught only
  at its PR, and only in a repo that has enabled the CI check. By then the
  branch is pushed, so the fix is a rename rather than a retry.
- The CI check blocks a merge by itself only where it is a required status
  check; otherwise it shows red, which the kit's `merge` skill already
  refuses.
- Consumers call the workflow from the kit's public repo. Were the kit made
  private, it would stay callable only by repos GitHub's access settings let
  in.
- Changing a rule means editing the constants and `git.md` together; nothing
  enforces it, so a PR changing one and not the other relies on review.
- The hook costs one `shlex` pass per Bash call, and two `git rev-parse` calls
  only when a non-conforming branch name is found.
- `just install` now registers two hooks through one prompt. An existing
  registration of the Stop hook is kept or rewritten in place as before.
- Anyone who has not re-run `just install` simply lacks the hook; nothing
  else depends on it.
- With agents refused here and everyone checked at the PR, the `pre-commit`
  check's only remaining value would be an earlier warning for humans. If
  that is ever wanted, it can call the hook's `--name` mode rather than
  copying the rules.

Later changes: ADR 047 moves the rules and the `--name` mode into
`hooks/conventions.py`, and renames the workflow `pr-conventions.yml`, with
`scripts/enable-pr-checks.sh` replacing `enable-branch-check.sh`.
