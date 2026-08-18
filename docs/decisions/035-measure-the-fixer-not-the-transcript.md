# 035 - Attribute formatter drift by measuring the fixer

Supersedes [ADR 024](024-stop-hook-for-formatter-drift.md).

## Decision

The hook keeps its two steps, but stops inferring authorship and stops deciding
what matters. `run_fixer` digests the working tree either side of the fix
command; the hook blocks whenever that command rewrote anything, and splits what
it rewrote two ways:

- **Committed** - paths the fixer dirtied that HEAD also tracks. They carried
  committed content until the fix landed, so the commit they came from no longer
  carries the reformat.
- **Uncommitted** - everything else it rewrote. Already modified, or not tracked
  at all, so the reformat joins the uncommitted work around it.

Reporting both, rather than blocking on one and staying silent on the other, is
the point: which of the two a change falls into is what Claude needs in order to
decide, and the hook has no business making that call.

The fixer runs on every turn, not only on turns that ended dirty. ADR 024's
single dirty-tree guard is gone - it meant a turn that committed everything ran
no fixer at all, which is precisely the turn whose formatting most needs
applying.

The hook is renamed `hooks/stop-autofix.py`, for what it does rather than for
what it used to detect, and the block's message is cut to a statement of what
the fixer changed - no numbered instructions.

Dropped from ADR 024: the "Claude did not write it itself" condition, the
`edited_since` transcript scan behind it, the session-start check, and the
dirty-tree guard. **The transcript is no longer read at all**, so the hook no
longer depends on an undocumented internal format. It is now purely a function
of the fix command's effect on the working tree.

## Reason

ADR 024's detect step asked two questions: is the file in this session's last
commit, and did Claude write it since? The second was answered by scanning the
transcript for `Edit`, `Write` and `NotebookEdit` tool calls. Two blind spots
make it answer "no" on ordinary work:

- A session can be configured to make file changes **through Bash** - `sed`,
  heredocs, short scripts - rather than the edit tools. Every such edit is
  invisible to the scan, so every file touched that way after a commit reads as
  drift. Observed: a conventions doc rewritten by a Python heredoc one commit
  later blocked the stop, with no formatter involved at all.
- **Subagents write their own transcript.** A file edited by a `push` or other
  subagent is unattributable from the parent's, in any mode.

Neither is fixable by parsing harder: which paths an arbitrary shell command
wrote is not recoverable from the command text. The fixer's own effect, by
contrast, is directly observable - and the hook was already snapshotting the
tree either side of the run, then discarding everything but a boolean. The
signal ADR 024 wanted was in hand the whole time; it just wasn't kept.

ADR 024's consequences claimed "The hook can go blind; it can't start firing
falsely." The Bash-mode case refutes that: the transcript parses cleanly and the
checks return a confident wrong answer.

Alternatives rejected:

- **Adding `Bash` to the watched tool set.** There is nothing to extract. A file
  path inside a shell command can't be recovered without interpreting the shell,
  and a script writing paths it computes at runtime defeats that outright.
- **Reading subagent transcripts as well.** Closes one blind spot and not the
  other, while deepening the dependence on an undocumented internal format that
  ADR 024 already flagged as a liability.
- **Downgrading the block to a `systemMessage`.** The turn has already ended
  when it lands, so the reformat stays uncommitted - exactly the orphaned diff
  ADR 024 exists to prevent. A block is still the only hook output that reaches
  Claude in time to be acted on.
- **Blocking only on the committed half, staying silent on the other.** Closer
  to ADR 024's instinct, and quieter. Rejected because a fixer rewriting
  uncommitted work is still something Claude should know before it writes a
  commit message for that work - and the split says which case it is, so the
  quiet is bought by withholding, not by precision.
- **Keeping inference as a second signal alongside measurement.** Any file it
  added would be one the fixer demonstrably didn't touch, so every extra hit is
  a guess - and guesses are what made the hook fire on ordinary turns.

## Consequences

- The fix command now runs at the end of every turn, including turns that
  changed nothing. That is the cost of covering the turn that commits
  everything, and it is real: a slow fixer is paid for on every stop, bounded
  only by the 120s timeout. Repos with an expensive fixer should make it
  incremental rather than set `fieldkit.fixCommand` to something whole-repo.
- Pre-existing formatting debt now surfaces. The first run in a repo that has
  never been fixed will list files nobody touched this session under
  "Committed", and will keep listing them every turn until they are committed
  or the repo is cleaned up. Arguably the right nag, but it is a behaviour
  change from ADR 024, where an untouched file could never appear.
- Formatting the hook didn't run - an editor's format-on-save, most likely - is
  not flagged. ADR 024 claimed that coverage, but it rested on the same broken
  inference, so what is genuinely lost is small. If it proves to matter, it
  needs a mechanism that observes the editor, not the transcript.
- False positives are structurally gone rather than reduced: the hook names only
  files it watched a command it ran rewrite, and says which side of the commit
  line each one falls on.
- **The transcript is no longer read.** ADR 024 accepted a dependency on an
  undocumented internal format and contained the risk; there is now no risk to
  contain. The hook reads nothing but git and the working tree.
- Snapshot cost is a `git diff --name-only HEAD`, a `git ls-files --others`, and
  a SHA-1 over the dirty and untracked files only, taken twice, plus one
  `git ls-tree` when something changed. Files matching HEAD are skipped, and
  their absence is load-bearing: a fixer rewriting one makes it appear in the
  second snapshot alone, which is exactly the committed-content signal.
- The block drops ADR 024's numbered instructions and its "say so and finish if
  it isn't formatter output" escape hatch, both of which existed because the old
  signal was a guess. `stop_hook_active` still caps this at one block per turn.
- `hooks/` gains no new dependency; the hook remains standard library only, and
  is down to 160 lines from 230.
- The rename would strand the command already in `~/.claude/settings.json`, so
  `register_stop_hook.py` matches a `LEGACY_HOOK_FILES` tuple beside the current
  name and rewrites the entry in place. Without it a re-register appends a
  second group pointing at a deleted file. Anyone not re-running `just install`
  keeps the old registration, which `|| true` renders inert rather than
  wedging their turns.
- Both groups were exercised end to end in a live session before merge, not
  only against scratch repos: a planted formatting error in a committed file
  and another in an uncommitted one, in the same turn, producing one block
  listing each under its own heading. The committed case needed the commit to
  land before the turn ended, since a background push that finishes later leaves
  the file dirty and the reformat lands in the other group instead.
- Testing "is this path in HEAD" is wrong, and was the first attempt: a tracked
  file under edit is in HEAD while the reformatted lines are not, so the hook
  fired on ordinary work in progress. The snapshot pair already tells the two
  apart - a path absent from the pre-fix snapshot matched HEAD until the fixer
  touched it - so the fix cost nothing but asking the right question. Found by
  running the hook for real against a planted formatting error, which is the
  only way it surfaced.
