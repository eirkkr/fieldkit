# 036 - Publish the kit under MIT with an upstream notice

## Decision

The kit is a public repository, MIT licensed, framed in its README as one
person's working setup published to be read rather than as a product. Content
vendored from or derived from OpenSpec is attributed in a top-level `NOTICE`
carrying that project's copyright and licence text.

## Reason

The conventions and the ADRs behind them are the parts that transfer to anyone
else's setup, and nothing here is secret - it is dev guidance and Claude Code
configuration, not application code. Publishing costs nothing and the ADRs are
worth more to a reader than the rules they justify.

MIT over Apache-2.0 or a Creative Commons content licence: the repo already
vendors and derives from MIT-licensed OpenSpec content, so matching that
licence removes any compatibility question. Apache-2.0's patent grant and
change-statement requirement buy nothing for a repo of prose, shell scripts,
and a justfile. A CC licence would fit the prose but not the scripts and hooks,
which would mean dual-licensing for no gain.

The `NOTICE` is an obligation, not courtesy. `repo-skills/` is upstream
generated content vendored verbatim, and `schemas/review-gated/` is a
derivative of the stock `spec-driven` schema
([ADR 034](034-review-gated-openspec-schema.md)); MIT requires the copyright
notice and licence text travel with both. The vendored skills' own frontmatter
already says `license: MIT`, but frontmatter in a generated file is not a
notice a reader of the repo will find.

Framing it as a personal kit rather than a reusable starting point matches what
it is: the conventions encode preferences, not general practice, and several
assume tooling choices (`just`, `uv`, `rumdl`) a fork would want to change.
Claiming general reusability would invite an adoption and support burden the
repo cannot honour.

## Consequences

- Setup instructions address a reader who has forked, since the `eirkkr/fieldkit`
  remote is not writable by anyone else; the "Updating a shared rule" section
  no longer assumes the reader is the owner.
- References to specific private consumer repos are genericised in the README
  and ADRs 004 and 034. New writing names a consumer by role ("a Python
  consumer"), not by name.
- `just openspec-refresh` regenerates `repo-skills/` from a newer upstream; if
  that upstream's licence ever changes, the `NOTICE` needs updating with it.
- `package.json` keeps `"private": true` - that blocks accidental `npm publish`
  and is unrelated to repository visibility.
