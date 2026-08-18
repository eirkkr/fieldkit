# 035 - Attribute formatter drift by measuring the fixer

Supersedes [ADR 024](024-stop-hook-for-formatter-drift.md).

## Decision

The hook keeps its two steps and its block, but stops inferring authorship.
`run_fixer` digests the working tree either side of the fix command. The hook
blocks when the fixer *dirtied* a path that had matched HEAD and that this
session's own last commit included - together, the two conditions that mean the
commit lost the reformat.

It is renamed `hooks/stop-autofix.py`, for what it does rather than for what it
used to detect, and the block's message is cut to a statement of what the fixer
changed. Deciding what that warrants - a commit, a test run, nothing - is
Claude's judgement, not the hook's script.

Dropped from ADR 024: the "Claude did not write it itself" condition and the
`edited_since` transcript scan behind it. The transcript is still read, for the
session's start time alone - a commit predating the session still means a dirty
tree is the user's own in-progress state, not something this session stranded.

Detection now covers only formatting the hook itself caused. Step 1, the block,
the single dirty-tree guard, and ADR 007's discarded fixer output are unchanged.

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
  ADR 024 exists to prevent. A block is still the only hook output that is an
  instruction rather than context.
- **Keeping inference as a second signal alongside measurement.** Any file it
  added would be one the fixer demonstrably didn't touch, so every extra hit is
  a guess - and guesses are what made the hook fire on ordinary turns.

## Consequences

- Formatting the hook didn't run - an editor's format-on-save, most likely - is
  no longer flagged. ADR 024 claimed that coverage, but it rested on the same
  broken inference, so what is genuinely lost is small. If it proves to matter,
  it needs a mechanism that observes the editor, not the transcript.
- False positives are structurally gone rather than reduced: the hook names only
  files it watched a command it ran rewrite. It can still go blind - an
  unreadable transcript degrades to silence as before.
- Snapshot cost is a `git diff --name-only HEAD`, a `git ls-files --others`, and
  a SHA-1 over the dirty and untracked files only, taken twice. Files matching
  HEAD are skipped: a fixer rewriting one makes it appear in the second snapshot
  alone, which reads as a change just the same.
- The block's wording now states the finding is measured, and drops ADR 024's
  "say so and finish if it isn't formatter output" escape hatch, which existed
  because the old signal was a guess. `stop_hook_active` still caps this at one
  block per turn.
- `hooks/` gains no new dependency; the hook remains standard library only.
- The rename would strand the command already in `~/.claude/settings.json`, so
  `register_stop_hook.py` matches a `LEGACY_HOOK_FILES` tuple beside the current
  name and rewrites the entry in place. Without it a re-register appends a
  second group pointing at a deleted file. Anyone not re-running `just install`
  keeps the old registration, which `|| true` renders inert rather than
  wedging their turns.
- The block no longer tells Claude to read the diff, re-run tests, and commit.
  ADR 024 scripted those steps because its signal was a guess that needed
  verifying; a measured one doesn't, and the standing conventions already cover
  what to do with an uncommitted change.
- Two conditions bound when the block can fire at all. The dirty-tree guard
  means a turn ending with everything committed runs no fixer, so it strands
  nothing; and the fixer has to dirty a file that was clean. Between them the
  block needs a session that committed a file, left the tree dirty by some other
  route, and then had the fixer rewrite the committed one. Narrower than
  ADR 024's framing suggests, and the first narrowing is the guard's, not this
  change's.
- Testing "is this path in HEAD" instead is wrong, and was the first attempt: a
  tracked file under edit is in HEAD while the reformatted lines are not, so the
  hook fired on ordinary work in progress. The snapshot pair already tells the
  two apart - a path absent from the pre-fix snapshot matched HEAD until the
  fixer touched it - so the fix cost nothing but asking the right question.
  Found by running the hook for real against a planted formatting error, which
  is the only way it surfaced.
