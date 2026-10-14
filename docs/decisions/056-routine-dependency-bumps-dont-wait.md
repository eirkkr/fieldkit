# 056 - Routine dependency bumps don't wait for confirmation

## Decision

`update-deps` sorts bumps into three tiers. **Routine** bumps - an indirect dependency, or a direct one's patch - get a cursory scan and land as their own commit without waiting. A direct **minor** gets the full review and waits for the user; a direct **major** is also flagged, and goes one at a time. An indirect dependency held back by its parent's cap is retried once the direct bumps land.

## Reason

The skill waited on every bump. In its first full run in a Python consumer, 21 of the 27 package bumps were routine - lock-only refreshes inside constraints the project or a parent had already chosen, with no decision for the user to make. They buried the waits that matter.

`just check` still gates the routine commit, and it lands apart from the rest, so a bad one is caught or reverted alone.

The retry comes from the same run: four indirect majors were unblocked by their parents' own bumps.

Alternatives rejected:

- **Confirm every bump.** The behaviour this replaces.
- **Confirm none.** A direct minor or major can change behaviour, and its review is where adoption gets decided.
- **Tier indirect bumps by semver too.** An indirect major is still bounded by its parent's cap.

## Consequences

- [ADR 043](043-python-skills-opt-in-per-repo.md)'s "the human confirming each bump" now holds for direct minors and majors only.
- A routine bump that changes behaviour without failing a test lands unreviewed.
