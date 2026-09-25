# CI conventions

See [ADR 048](../docs/decisions/048-pin-ci-by-commit.md) for the reasoning.

## Pin everything a workflow runs on

Nothing a workflow depends on changes without a commit saying so.

- **Actions:** the full commit SHA, with the version as a trailing comment:

  ```yaml
  - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0
  ```

  Not `@v4`, which moves with every 4.x release, and not `@v4.4.0`, since a
  tag can be re-pointed. A commit can't. Dependabot and Renovate both update
  this form, comment included.
- **Runners:** a versioned image such as `ubuntu-24.04`, never `-latest`.
- **Tools a job installs:** an exact version, such as
  `uv tool install rust-just@1.58.0` - never an unversioned install or a
  `curl | bash` script.

Find an action's commit from its release tag - this resolves annotated tags
too:

```bash
gh api repos/<owner>/<action>/commits/<tag> -q .sha
```

Upgrading means editing the pin: change the SHA and its comment together.
