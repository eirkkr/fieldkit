# Building AI / LLM features

For features that call a language model. The goal is output that is
reproducible where it can be, bounded, auditable, and cheap.

## Where AI belongs

- Prefer deterministic code. Reach for an AI stage only where the work needs
  genuine judgment or natural-language understanding that resists
  codification; mechanical transformation, validation, and rendering are not
  AI work.
- Decouple expensive generation from cheap rendering, so cosmetic or local
  changes do not re-invoke the model.

## Bounding an AI stage

- Give it the smallest tool set it needs; no network/browse tools unless the
  feature genuinely requires them.
- Have it read only its named inputs and emit exactly its contract artifact -
  no wandering, no extra output.
- Keep its knowledge self-contained (in-repo references) rather than dependent
  on external lookups or the model's own training-data recall where
  correctness matters.
- Pursue stable, bounded output by whatever means the backend actually
  exposes. Where sampling controls are available, use a low temperature -
  but do not assume they are: some current models reject `temperature`/
  `top_p`/`top_k` outright. On those, effort/reasoning-level settings (where
  offered) are the tuning knob, and the mandatory gate below (not the
  sampling parameters) is what actually makes the output trustworthy. Don't
  claim a stability guarantee from temperature alone; verify what your
  chosen model accepts before relying on it.

## Untrusted input

- Treat any user-supplied free text fed to a model as untrusted: delimit it as
  data, instruct the model to ignore instructions embedded in it, and
  schema-validate the output, discarding anything off-schema. (Prompt
  injection.)

## Trust but verify

- Gate non-deterministic output with a **deterministic checker** that doubles
  as the regression oracle in tests. Keep model-calling evals out of blocking
  CI (they cost tokens and vary); run them on demand or on a schedule.
- Stamp **provenance** on generated artifacts - model id plus the versions of
  any config/knowledge used - so a result can be explained and debugged later.
- Measure per-call token cost before relying on or pricing the feature.
