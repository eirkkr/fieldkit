# Working conventions

- When proposing new doc/convention text, show it and wait for approval before
  editing.
- Record non-obvious conventions in CLAUDE.md / docs, not machine-local memory
  (memory isn't available on other machines or to other developers).
- Before any suppression (`# type: ignore`, `# noqa`, tool exclusion), check
  whether the underlying issue can be fixed instead. Suppress only when the tool
  is genuinely wrong about the file's context.
