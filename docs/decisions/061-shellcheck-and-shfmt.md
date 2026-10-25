# 061 - Lint shell scripts with shellcheck and shfmt

## Decision

Shell scripts, in the kit and in consumer repos, are linted with shellcheck and formatted with shfmt, both run by `just lint` and shfmt also by `just fix`. They are pinned through uv, as the `shellcheck-py` and `shfmt-py` packages. shfmt's style lives in a root `.editorconfig`. The kit recommends an indent - four spaces with indented `case` arms, its own - but leaves the choice to each repo. The rules are in [ci.md](../../conventions/ci.md)'s "Shell scripts".

## Reason

Consumer repos keep shell scripts - check scripts, a Docker entrypoint, release tooling - and the kit said nothing about checking them, so each repo decided alone or skipped it. A Python consumer adopted the pair first: its 6 scripts, about 500 lines, needed one suppression and no reformat.

shellcheck and shfmt are the de facto pair, and neither has a close rival. Rejected:

- **bashate or beautysh.** Both check or fix style only; neither finds the bugs shellcheck does.
- **A meta-linter (super-linter, MegaLinter).** Each runs these same two tools inside a large container image, adding an image pull to every run and a second layer of configuration.
- **The vendors' own binaries.** A download script or a release asset puts a third-party host on every run; the uv packages pin like every other tool the kit runs ([ci.md](../../conventions/ci.md), "Pin everything a workflow runs on").
- **A kit-wide indent.** A repo already formatted another way would need a reformat for no gain in correctness. Four spaces with indented `case` arms matched every script in the consumer and 15 of the kit's 19, so it is the recommended starting point.

`/kit-reconcile` does not flag a consumer with shell scripts and no shell check: it reconciles agent instructions and leaves a repo's linters to the human.

## Consequences

- A repo adopting the convention adds a check script, a `.editorconfig` and an empty `.shellcheckrc`; the kit's `scripts/check-shell.sh` is a worked example.
- The packages' wheels carry the binaries and are tagged `py2.py3-none-<platform>`, so they install on any Python 3 and never hold up a Python upgrade.
- shellcheck-py has no Linux ARM64 wheel, so on that platform its sdist downloads the pinned shellcheck release from GitHub at install.
- shfmt-py numbers its own releases, so a pin bump checks which shfmt the package ships.
