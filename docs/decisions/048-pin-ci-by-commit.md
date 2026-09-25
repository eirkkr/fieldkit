# 048 - Pin CI actions by commit, runners and tools by version

## Decision

Everything a CI workflow runs on is pinned, per `conventions/ci.md`: actions
by full commit SHA with the version as a trailing comment, runners by a
versioned image, and tools a job installs by exact version.

## Reason

An unpinned dependency changes a workflow without any commit in the repo
saying so, and a failure it causes looks like the repo's own fault.

For actions there are three ways to reference a version:

- **A major tag, `@v4`.** The action's maintainers move it to each 4.x
  release, so it drifts within a major version the way `-latest` drifts
  across them. Some actions no longer publish one: `setup-uv` has `v6` and
  `v7` tags, but none from `v8` on.
- **An exact tag, `@v4.4.0`.** Readable, but a git tag can be re-pointed, so
  it pins by convention rather than by construction.
- **A commit SHA.** Cannot move. GitHub's security hardening guide names it
  the only immutable reference to an action. The trailing `# v4.4.0` keeps it
  readable, and Dependabot and Renovate update the pair together.

The SHA is the only one of the three that is actually a pin.

Runners have no finer pin than the OS version: `ubuntu-24.04` stops the move
to the next release, while GitHub still refreshes the image's packages
roughly weekly.

## Consequences

- Nothing upgrades on its own. Without a bot proposing bumps, each upgrade is
  a manual edit of the SHA and its comment.
- A pinned action misses security fixes until someone bumps it - the price
  of it not changing unannounced.
- Consumer repos meet the rule through `kit-reconcile`, which lists existing
  workflows that break it as follow-ups.
