# 056 - Routine dependency bumps don't wait for confirmation

## Decision

`update-deps` sorts each outdated package into one of three tiers by what its bump can break, using the version boundaries in `conventions/python/setup.md`:

- **Routine** - an indirect dependency, or a patch bump of a direct one. It gets a cursory changelog scan, is bumped without waiting, and lands as its own commit after `just check` passes.
- **Minor** - a direct dependency's minor bump: the full changelog review, then the user confirms.
- **Major** - a direct dependency's major bump: the full review, flagged, then the user confirms, one at a time.

An indirect dependency held back by its parent's cap is retried once the direct bumps land.

## Reason

The skill waited for confirmation on every bump, and in its first full run in a Python consumer, 21 of the 27 package bumps were indirect dependencies or direct patches nobody had a view on. An indirect bump or a direct patch refreshes the lock inside constraints already chosen, by the project or by a parent, so there is no decision for the user to make. The waits that matter - a direct minor's new behaviour, a major's breaking changes - were buried among the ones that don't.

`just check` still runs before the routine bumps are committed, so one that breaks the suite never lands. They commit apart from the rest, so one that slips through reverts alone.

The retry comes from the same run: four indirect majors sat outside their parents' caps until the parents' own bumps lifted them. Reporting them as blocked would have left them stale for no reason.

Alternatives rejected:

- **Confirm every bump.** The original behaviour, rejected above.
- **Bump everything without waiting.** A direct minor or major can change behaviour the codebase relies on, and its changelog review is where an adoption decision gets made. That stays with the user.
- **Tier by semver alone, direct and indirect alike.** An indirect package's major is still bounded by its parent's cap, which the parent's maintainers chose; it needs no more scrutiny than its parent's own bump.

## Consequences

- [ADR 043](043-python-skills-opt-in-per-repo.md)'s "the human confirming each bump" now holds for direct minors and majors only.
- A routine bump that changes behaviour without breaking a test lands unreviewed. The cursory scan is what stands between it and the branch.
- A date-versioned direct dependency (`regex`'s `2026.9.29`) has no patch to read, so it is a minor.
