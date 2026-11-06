# Building AI / LLM features

For features that call a language model. Aim for output that is reproducible where possible, bounded, auditable and cheap.

## Where AI belongs

- Prefer deterministic code. Use an AI stage only for judgment or natural-language understanding that resists codification; transformation, validation and rendering are not AI work.
- Decouple expensive generation from cheap rendering, so cosmetic or local changes don't re-invoke the model.

## Bounding an AI stage

- Give it the smallest tool set it needs; no network or browse tools unless the feature requires them.
- It reads only its named inputs and emits exactly its contract artifact.
- Where correctness matters, keep its knowledge in-repo rather than in external lookups or training-data recall.
- Use a low temperature where sampling controls exist, after verifying what the model accepts: some current models reject `temperature`, `top_p` and `top_k` outright, leaving effort or reasoning-level settings as the knob. Either way the deterministic checker below, not a sampling parameter, makes the output trustworthy.

## Untrusted input

- Treat user-supplied free text fed to a model as untrusted (prompt injection): delimit it as data, tell the model to ignore instructions embedded in it, and schema-validate the output, discarding anything off-schema.

## Trust but verify

- Gate non-deterministic output with a **deterministic checker** that doubles as the tests' regression oracle. Keep model-calling evals out of blocking CI (costly, variable); run them on demand or on a schedule.
- Stamp **provenance** on generated artifacts (model id, plus versions of any config or knowledge used) so a result can be explained later.
- Measure per-call token cost before relying on or pricing the feature.
