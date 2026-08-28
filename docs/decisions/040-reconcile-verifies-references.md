# 040 - Verify the consumer's references into the kit on every reconcile

## Decision

`/kit-reconcile` verifies that this repo's references into the kit still
resolve, as its first step and independently of the commit range it goes on to
review. The check covers the `.fieldkit` symlink, every `@.fieldkit/...` import
reachable from the repo's `CLAUDE.md`, every other `.fieldkit/...` path named
in a tracked file, and any symlink into the kit that now dangles. An
unresolved reference is a finding fixed in that run, not a warning reported
onward.

## Reason

The reconcile step audits agent-facing docs "for anything that now contradicts
the kit" - stale instructions. A broken reference is a different failure. A
stale instruction still loads and quietly says the wrong thing; an unresolved
import doesn't load at all, so the session runs with rules *missing* rather
than wrong, and the session least placed to notice is the reconcile session
itself, since the import that failed is the one that would have told it how to
behave.

Renaming the shared entry point to `KIT.md`
([037](037-split-kit-entry-from-own-rules.md)) invalidated every consumer's
`@.fieldkit/CLAUDE.md` line in a single commit. That commit is marked
`BREAKING:` and the README carries a migration note, so a reconcile reading the
history would most likely have caught it - but by inference from prose, not
because anything checked whether the import resolved. Running the check whatever
the range also catches a break from a kit commit the marker has already passed,
or from a botched local edit; neither appears in `<marker>..main`.

Alternatives rejected:

- **Sweep only the repo's `CLAUDE.md`.** That is the file whose breakage costs
  a session its rules, so it is the minimum. But the wider sweep is one `grep`
  over tracked files, and it catches READMEs, scripts and `.claude/` config
  that name kit paths - the same one-line fix, found in the same pass.
- **Make it a session-start hook instead.** A resolve-check is exactly what one
  would want run at session start, and a hook would catch the breakage in the
  session that suffers it rather than at the next reconcile. It is also a
  bigger change than this: a hook has to be installed per consumer, has to
  decide what to do about a finding it cannot fix, and adds startup cost to
  every session to catch a fault that only a kit-side rename or a local edit
  produces. The reconcile is where kit-side renames are already being read, so
  it gets the check first; a hook remains open as a follow-up if the reconcile
  proves too late a place to find these.
- **Report an unresolved reference and move on.** The fix is usually a one-line
  path change, and the information needed to make it - the kit history for the
  range - is already in hand.

## Consequences

- A reconcile can now produce a fix with an empty commit range: the references
  are checked whatever the range says, so a run that reviews no new kit commits
  may still change a path. The marker bump still happens either way.
- The wider sweep can turn up `.fieldkit/...` paths in human-facing docs. Those
  are corrected as paths; the reconcile still leaves human tooling itself alone.
- The check knows the kit's current layout only through the checkout it is
  reading, so a reference that resolves is not proof the target still says what
  the repo assumed - that remains the audit's job.
