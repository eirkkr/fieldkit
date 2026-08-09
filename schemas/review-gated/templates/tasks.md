## 1. Stage 1 - <!-- one idea, named -->

<!-- 1-3 sentences: what this stage delivers, and what must be true before
     stage 2 starts. -->

- [ ] 1.1 <!-- One action, naming the file(s). Done when <checkable
      condition>. -->
- [ ] 1.2 <!-- ... -->
- [ ] 1.3 REVIEW GATE - stage 1. Stop here. Do not tick this box, and do not
      begin stage 2, until the reviewer approves. Write the review note below
      first.

## 2. Stage 2 - <!-- one idea, named -->

<!-- 1-3 sentences. -->

- [ ] 2.1 <!-- ... -->
- [ ] 2.2 <!-- ... -->
- [ ] 2.3 REVIEW GATE - stage 2. Stop here. Do not tick this box, and do not
      begin stage 3, until the reviewer approves. Write the review note below
      first.

<!-- ... more stages. Aim for 3-6 tasks each, 8 at the most. Prefer more,
     smaller stages: a smaller stage is a cheaper review. -->

## 3. Stage 3 - final review

The whole change, checked against its own spec, together with the reviewer.
Iterate until they are satisfied.

- [ ] 3.1 Re-read proposal.md, design.md and every delta spec against what
      was actually built. List each requirement and where it is satisfied in
      the code. Flag any that is unmet, partly met, or met differently than
      specified.
- [ ] 3.2 List everything built that no requirement asked for, and everything
      the artifacts still describe that was not built. Either the code or the
      artifacts is wrong - say which.
- [ ] 3.3 Update the artifacts so they describe what was actually built,
      including decisions that changed mid-flight. Record anything durable as
      an ADR rather than leaving it in design.md.
- [ ] 3.4 Walk the full diff for the conventions CI cannot check.
- [ ] 3.5 FINAL REVIEW - present the change as a whole and iterate with the
      reviewer until they are satisfied. Stop here. Only the reviewer closes
      this box.
