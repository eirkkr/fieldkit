# 046 - Refuse non-conforming branch names in a PreToolUse hook

## Decision

The kit ships `hooks/pretooluse-branch-name.py`, a Claude Code `PreToolUse`
hook on `Bash`. It refuses a command that creates or renames a branch to a
name outside the prefixes `conventions/git.md` allows, through the documented
JSON `deny` decision, with a reason naming the allowed prefixes and pointing
at `git.md`.

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
- **One copy of the prefixes.** The hook reads them from `git.md`'s "Allowed
  prefixes:" bullet at run time. `--prefixes` prints what it reads, and
  `just check` fails when that is empty.
- **`EnterWorktree` is left out.** Its input carries a worktree `name`, not a
  branch name; the branch Claude Code derives from it is not in the tool's
  schema.
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

It complements the `pre-commit` check proposed for branch names rather than
replacing it: that one fires at the first commit and catches everyone, this
one fires earlier and catches only Claude. That split is also what makes the
`pre-commit` check's "refuse for agents, warn for humans" option reachable -
there was no signal for "an agent is committing", and a `PreToolUse` hook is
one. With agents refused here, the `pre-commit` check is free to warn.

Why the choices above:

- **Failing open** over refusing when unsure: a missed catch is no worse than
  having no hook, while a false refusal blocks legitimate work, possibly in a
  way Claude can't route around without help.
- **Scoping to kit repos:** registration is machine-wide, but the naming rule
  is the kit's, not a universal one. Imposing it on an unrelated repo - a
  third-party checkout, a repo with its own naming scheme - would be a false
  refusal by definition. The main worktree is checked as well as the current
  one because `.fieldkit` is gitignored, so a linked worktree never has it.
- **Parsing `git.md`** over a separate data file: the doc is where a human
  reads the rule, and a second copy anywhere drifts from it. The cost is that
  rewording the bullet could silently disable the hook, which is what the
  `just check` guard exists to catch. A data file the doc points at was
  rejected because it takes the list out of the doc people actually read.
- **Checking prefixes only**, not lowercase or hyphenation: the prefix set is
  closed and mechanical, the style rules are looser and more likely to
  refuse a name a human would accept.
- **One registration script** over a second copy of the Stop one: the two
  would differ only in event, matcher and file name, and the legacy-rename
  handling from ADR 035 would otherwise be duplicated.

Alternatives rejected:

- **Only the `pre-commit` check.** Fires after work has piled up on the
  wrongly named branch, and cannot tell an agent from a human, forcing one
  refuse-or-warn answer on both.
- **A non-zero exit to refuse.** Indistinguishable from a crash, which must
  fail open; the JSON decision is the documented block.
- **Guessing `EnterWorktree`'s branch name.** It would hard-code an
  undocumented naming scheme that can change under the hook, and a name
  Claude doesn't choose directly isn't the failure being fixed.

## Consequences

- Claude's branch creation through Bash in a kit repo is checked; a human's,
  and anything made by `EnterWorktree` or a tool other than Bash, is not.
- The "Allowed prefixes:" bullet in `git.md` is now load-bearing: it must
  stay one bullet listing the prefixes in backticks before its first period.
  `just check` enforces that it still parses.
- The hook costs one `shlex` pass per Bash call, and two `git rev-parse` calls
  only when a non-conforming branch name is found.
- `just install` now registers two hooks through one prompt. An existing
  registration of the Stop hook is kept or rewritten in place as before.
- Anyone who has not re-run `just install` simply lacks the hook; nothing
  else depends on it.
- The `pre-commit` check can read the same bullet, keeping the one copy, when
  it is built.
