# Which rules must a coding agent follow in this repository?

## Which rules has our team set?

These rules are grounded in `BRIEF.md`, `docs/EVALUATION_CONTRACT.md`, `docs/ROLES.md`, `docs/LADDER.md` and `src/README.md`.

1. **Never modify `src/contract.py`.** It contains the client's scoring rules. Import and use its functions and constants instead of changing or copying its formulas.
2. **Keep the date split exact.** Train on arrivals before `2016-07-01`, choose settings on arrivals from `2016-07-01` to `2016-12-31`, and reserve arrivals from `2017-01-01` onward for the final proof.
3. **Never tune on proof data.** Freeze the model settings and buffer before the proof run. If anything changes after seeing proof results, document the change and report both runs.
4. **Use only information available when a booking is made for the MVP.** Follow the first-bin decisions in `docs/COLUMNS.md`. Never use post-outcome columns such as `reservation_status` or `reservation_status_date` as predictors.
5. **Keep the target out of the features.** `is_canceled` is the outcome to predict, not an input feature. Do not introduce target leakage.
6. **Keep predictions aligned with booking rows.** Every cancellation probability must correspond to the correct booking and row order passed to `nightly_table`. Probabilities must be finite and between 0 and 1.
7. **Make decisions at hotel-arrival-night level.** Aggregate booking probabilities by `hotel` and `arrival_date` using the supplied contract helpers. Oversell counts must be non-negative whole numbers.
8. **Choose the buffer on the choose period and freeze it.** Never select or adjust the buffer using proof-period results.
9. **Always compare against the client's flat-rule baseline.** Use each hotel's train-period cancellation rate and a fixed safety margin selected on the choose period under the same walk ceiling.
10. **Treat the walk ceiling as mandatory.** A policy exceeding 10 walked guests per 1,000 arrivals is rejected, even if it saves money. Report euros, empty rooms, walked guests and walks per 1,000 together.
11. **Keep `src/nightly.py` reproducible.** It must load the saved model and settings from `models/`, produce the requested nightly table, and must not retrain models or reselect buffers.
12. **Agree interfaces before depending on them.** Confirm function names, input/output columns, file paths and saved-model format with the Data Lead and Model Lead. Record important decisions in `docs/DECISIONS.md`.
13. **Make focused changes only.** Do not refactor unrelated files, add unnecessary dependencies or modify files owned by teammates without coordinating with them.
14. **Test before committing.** Run relevant tests, including `pytest -q`. When the pipeline is ready, verify both commands in `src/README.md`. Never claim a test passed unless it was actually run.
15. **Keep secrets and local files out of Git.** Never commit API keys, passwords, virtual environments, caches or unrelated generated files.

## Which general coding guidelines apply?

Append Andrej Karpathy's coding guidelines using the command documented in `docs/AI_WORKFLOW.md`. Keep these project-specific rules above the general guidelines.

## General AI Coding Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.

- If multiple interpretations exist, present them - don't pick silently.

- If a simpler approach exists, say so. Push back when warranted.

- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.

- No abstractions for single-use code.

- No "flexibility" or "configurability" that wasn't requested.

- No error handling for impossible scenarios.

- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.

- Don't refactor things that aren't broken.

- Match existing style, even if you'd do it differently.

- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.

- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.
