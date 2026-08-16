## Review gates (kit overlay - overrides the above)

Where this section and anything above it disagree, this section wins.

Under the `review-gated` schema, an unfinished review is a harder blocker
than an unfinished task. Step 3's "warn, confirm, proceed" handling is not
enough for these two cases.

Before archiving, read the tasks file and check:

- **An open review gate** (a `- [ ]` task whose text contains `REVIEW GATE`)
  means a stage was never signed off.
- **An open final review** (a `- [ ]` task whose text contains
  `FINAL REVIEW`) means the whole-change review never happened, or the
  reviewer never declared themselves satisfied.

In either case, do not archive. Report which gates are open, and point at
`/openspec-apply-change` to finish them. The user may still override by
saying so explicitly - but ask, rather than folding this into the generic
incomplete-tasks confirmation, and name what is being skipped.

A PR still in draft is a softer signal of the same thing: the final stage
takes it out of draft once the reviewer is satisfied, so a draft PR on the
branch suggests that step never ran. Mention it; it does not block.

The final review is also where the delta specs were reconciled against what
was actually built (its stage does that as a task). If it is closed, step 4's
sync assessment should find the specs already accurate; a large surprise
delta there is a sign the final review was rushed, and worth saying so.
