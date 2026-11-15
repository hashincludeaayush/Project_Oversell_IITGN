# Phase 8 Findings: Leakage and AUC Experiment

**Owner:** Data Lead  
**Date:** 2026-11-15  
**Evidence:** `src/phase8_leakage_auc.py`, `notebooks/05_leakage_auc_experiment.ipynb`

## Objective

Measure cancellation-ranking performance using valid booking-time information,
demonstrate the effect of outcome leakage, and quantify the optimism caused by
a random split.

## Controlled runs

The same logistic-regression pipeline, target (`is_canceled`) and AUC metric
were used in every run.

| Run | Features | Split | AUC | Interpretation |
|---|---|---|---:|---|
| A | Approved Bin 1 predictors | Chronological train/proof | 0.8184 | Primary MVP evidence |
| B | All non-target raw columns | Chronological train/proof | 1.0000 | Leakage diagnostic only |
| C | Approved Bin 1 predictors | Stratified random 80/20 | 0.8795 | Sensitivity check only |

## Findings

1. Run A achieved an AUC of **0.8184** using only the 23 approved booking-time
   predictors.
2. Run B achieved **1.0000**, demonstrating that including amendable and
   after-the-fact fields creates an invalid, artificially perfect result.
3. Run C achieved **0.8795**, higher than the chronological result, showing why
   random splitting must not be the primary estimate for this time-ordered
   problem.

## Decision

The team should use Run A as the trustworthy Phase 8 result. The MVP must use
the approved Bin 1 feature set and chronological evaluation. Run B must never
be used for production, and Run C must not replace the chronological result.

These AUC results measure ranking quality only. Model and buffer selection must
still use the official business-cost contract, including empty rooms, walked
guests, euros, and the 10 walks-per-1,000 ceiling.

## Validation

- `python src/phase8_leakage_auc.py` completed successfully.
- `python -m pytest -q tests/test_features.py` passed: 4 tests.
- `src/contract.py` was not modified.
