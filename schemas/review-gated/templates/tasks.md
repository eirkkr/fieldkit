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

- [ ] 3.1 Walk the full diff for the conventions CI cannot check. Done
      before the artifacts are touched - the walk turns up artifact-shaped
      findings.
- [ ] 3.2 Re-read proposal.md, design.md and every delta spec against what
      was actually built. List each requirement and where it is satisfied in
      the code. Flag any that is unmet, partly met, or met differently than
      specified.
- [ ] 3.3 List everything built that no requirement asked for, and everything
      the artifacts still describe that was not built. Either the code or the
      artifacts is wrong - say which.
- [ ] 3.4 List every requirement that holds only by construction, with no
      test behind it, and say what would have to be written to verify it.
- [ ] 3.5 Re-read every issue the change references - in the artifacts, in
      docstrings, in the docs it touches. Done when each is confirmed still
      open and still about the thing cited, or the reference is fixed.
- [ ] 3.6 Update the artifacts so they describe what was actually built,
      including decisions that changed mid-flight and anything 3.1-3.5
      found. Record anything durable as an ADR rather than leaving it in
      design.md.
- [ ] 3.7 FINAL REVIEW - present the change as a whole and iterate with the
      reviewer until they are satisfied. The note opens with two diffs: since
      the last approval, then the whole change, each naming its base commit.
      Stop here. Only the reviewer closes this box.
- [ ] 3.8 Mark the PR ready for review and bring its description up to the
      finished change. Done when it is no longer a draft.
