# 024 - Fix and catch formatter drift in one Stop hook

## Decision

The kit ships a Claude Code `Stop` hook, `hooks/stop-format-drift.py`, that
runs two steps in one process as a turn ends:

1. **Fix.** If the repo names a command in the `fieldkit.fixCommand` git
   config, run it. Its output is discarded, never fed back to the agent. Repos
   that set nothing skip this entirely.
2. **Detect.** Block the stop when the working tree holds changes to files
   *this session's own last commit already included* that *Claude did not write
   itself since that commit*. That conjunction is the signature of a formatter
   or linter - step 1's, or an editor's format-on-save - rewriting committed
   work. The block's reason tells Claude to read the diff, re-run affected
   tests, and commit and push it, and to say so and finish if it judges the
   change isn't formatter output.

The detect step never formats and never commits. A single dirty-tree guard
(`git status --porcelain`) covers both steps, per
[ADR 007](007-agents-dont-run-linters.md)'s reasoning against an
extension-based guard.

The hook is registered machine-wide in `~/.claude/settings.json` by
`just install` (`scripts/register-stop-hook.sh`), alongside the statusline and
attribution steps. The mechanism is the kit's; the command is the repo's.

It lives in `hooks/` beside the `pre-commit` hook from
[ADR 023](023-block-default-branch-commits-via-hook.md). The directory is named
for what its files are, not for who installs them; the two are distinguished by
filename, and `enable-hooks.sh` links only `pre-commit`.

## Reason

A formatter can rewrite a file *after* Claude edited it, and often after Claude
has already committed and pushed for the turn - orphaning the diff until
something else prompts a fresh `git status`. Claude Code surfaces external
modifications as a passive system-reminder, but the text is fixed product
behaviour and it can arrive too late to act on. This happened twice in one
rundrafter session, each time needing the human to notice and ask for a
follow-up commit.

The turn's end is the only moment that reliably comes after the formatter has
run, so `Stop` is the right event. A block is the only hook output that is an
instruction rather than context: it keeps Claude's judgement in the loop - test
verification, a real commit message - instead of a blind auto-commit.

**Why one hook rather than two.** rundrafter already had a repo-level `Stop`
hook running `just fix`, and it was the likeliest source of the very drift that
motivated this: it fires after the turn's commit and push, applies fixes, and
reports them to the human only, never to the agent. Claude Code merges hooks
across user, project, and local settings and **runs all of an event's matching
hooks in parallel**, so a separate detector could not be ordered after it. It
would sample `git status` while `just fix` was still writing - usually missing
the drift, occasionally reading a half-written file. Two hooks cannot be
sequenced; one process can. So the fixer becomes a step, and ordering is
deterministic by construction.

**Why this doesn't reopen ADR 007.** That decision keeps *the agent* out of the
run-lint-parse-fix loop; it doesn't forbid a machine from formatting. The hook
runs the fixer, discards its output, and never hands lint findings to Claude.
Its own consequences already named "a per-repo silent auto-fix hook, documented
as opt-in" as the sanctioned path and argued for on-stop timing; this is that
hook. What ADR 007 rejected was the kit owning a *format command* - and it
still doesn't. The kit owns the mechanism, the repo names its own command.

Alternatives rejected:

- **A `PostToolUse` hook injecting `additionalContext`.** Soft context, not a
  guaranteed instruction, so the model may not act on it. It also races the
  formatter, which doesn't run on Claude's tool-call schedule - the reformat
  frequently lands after the last tool call of the turn.
- **A git-only check: dirty files intersected with the last commit's files.**
  No dependence on the transcript, and much shorter. Rejected because it can't
  tell a formatter's rewrite from Claude editing a previously-committed file
  again, which is the ordinary act-then-show flow - it would block on nearly
  every editing turn and demand a commit for work the user hasn't asked to
  save. Consulting what Claude itself wrote since the commit is what makes the
  signal specific.
- **A blind auto-commit of the fixer's output.** Cheapest, and never nags.
  Rejected because it commits unreviewed changes with a generic message and
  skips test verification - `fieldkit.fixCommand` covers lint autofixes too, so
  the change may be more than whitespace.
- **Naming the fix command in a committed file rather than git config.** It
  would travel with the repo instead of being per-clone, and show up in review.
  Rejected on trust: a machine-wide hook that executes a command read from repo
  content would run arbitrary code from any repo you cloned and opened. Git
  config can only be set by the person holding the clone.
- **Keeping the fixer per-repo in `.claude/settings.json`.** Status quo in
  rundrafter, and it needs no kit change. Rejected because it is precisely the
  arrangement that races, and because the fixer's output reaches only the
  human - the orphaned-diff problem is structural to it.
- **Opting the whole hook in per repo via `enable-hooks.sh`.** Settings hooks
  live under `~/.claude`, machine-level state - the same line ADR 023 drew when
  it kept `.git/hooks` out of `just install`. The guards make the hook a silent
  no-op wherever it doesn't apply, so there's nothing to opt out of.
- **Splitting `hooks/` into `hooks/git/` and `hooks/claude/`.** Tidier, but
  moving `pre-commit` would leave every already-installed
  `.git/hooks/pre-commit` symlink dangling, and git skips a dangling hook
  silently - default-branch protection would disappear with no error.

## Consequences

- The detect step reads the session transcript JSONL, an internal format with
  no compatibility guarantee. Contained deliberately: the full parse runs only
  after the git checks have already found drift, and every failure path -
  unreadable transcript, unparsable line, missing timestamp - degrades to
  silence. The hook can go blind; it can't start firing falsely.
- Cost on the common case is one `git status --porcelain`. A turn that ends
  clean runs neither step.
- `fieldkit.fixCommand` is per clone, like `fieldkit.defaultBranch`
  (ADR 023), so a fresh checkout formats nothing until it is set again. Unlike
  `defaultBranch` there is no sane fallback to guess, so the loss is silent -
  accepted as the cost of not executing repo-supplied commands. Repos that want
  it should say so in their own setup docs.
- The fix command runs through a shell, with output discarded, a 120s timeout,
  and failures ignored - a broken or hanging fixer can never block the turn.
- A repo with its own fixer migrates through `/kit-reconcile`, which already
  covers "any repo-side change the new rules imply - commands, recipes,
  config"; its exclusion of the linters themselves doesn't apply, since the fix
  recipe stays and only the hook invoking it goes. rundrafter's migration is
  deleting `.claude/hooks/auto-fix.sh` and its `.claude/settings.json` `Stop`
  entry. Until it runs, both hooks fire and the race stands; every other repo
  gets the detect step alone, which is correct on its own.
- Order that migration carefully: merge here, rerun `just install`, set
  `fieldkit.fixCommand`, and only then remove the repo's own hook. Reversed,
  there's a window with no fixer at all.
- Being git config, `fieldkit.fixCommand` can't ride along in the reconcile PR
  the way a committed file would - the trust argument above is paid for here.
  A repo should carry the setting in a `setup`-style recipe instead: the
  command stays version-controlled and reviewable, but a human still runs it,
  so nothing is auto-executed from repo content.
- A human editing a just-committed file in their editor mid-turn reads as
  drift and gets blocked. Accepted: the reason explicitly offers "say so and
  finish", and `stop_hook_active` is honoured, so it costs one turn and can't
  loop.
- Honouring `stop_hook_active` skips *both* steps, so the turn Claude spends
  committing the drift runs no fixer. Anything it writes there is fixed on the
  next ordinary turn.
- A merge commit at `HEAD` lists no files under `git show --name-only`, so
  drift on top of one isn't caught. Rare enough not to warrant a special case
  that diffs against both parents.
- Registration is per machine and needs a `just install` rerun on an existing
  install, like every other `~/.claude` step.
- The registered command ends in `|| true`. A `Stop` hook exiting non-zero is
  read as a blocking error, and the registered path points into a working tree
  whose contents vary by branch - so checking out a branch that predates the
  hook file makes `python3` exit 2 and blocks every turn with a file-not-found
  message until the branch is switched back. Since the hook signals a genuine
  block through stdout JSON and never through its exit code, treating every
  non-zero exit as inert loses nothing and removes a way to wedge a session.
- Only `Edit`, `Write`, and `NotebookEdit` count as Claude's own writes. A file
  Claude changes by running a command in `Bash` looks external and can trigger
  a block - correct often enough (a generator's output does belong in a commit)
  to leave as is.
