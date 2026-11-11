
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

