# Phases 6–7 findings: cleaning and feature preparation

**Date:** 2026-11-11  
**Analyst:** Aayush Singh, Data Lead

## Cleaning decisions

The raw export is never mutated. `src/features.py` returns a prepared copy:

| Field | Observation | Prepared representation |
|---|---:|---|
| `children` | 4 missing rows | Fill with `0` as a guest count |
| `country` | 488 missing rows | Fill with `Unknown` |
| `agent` | 16,340 missing rows | Fill with `No agent` |
| `company` | 112,593 missing rows | Fill with `No company` |
| Exact duplicates | 31,994 duplicate rows; 40,165 rows in duplicate groups | Retain; do not alter the raw/scoring export |
| Zero-night bookings | 715 rows | Retain for contract scoring; flag for later review |
| Zero-ADR bookings | 1,959 rows | Retain for contract scoring; `adr` is not an MVP predictor |
| Negative ADR | 1 row | Retain for contract scoring; flag for later review |

## Feature contract

[features.py](../src/features.py) defines 23 Bin 1 model features in `MODEL_FEATURES`. It derives `arrival_date` and `nights`, keeps scoring columns separate, and excludes `is_canceled`, `reservation_status`, and `reservation_status_date` from predictors.

The function `prepare_bookings()` does not mutate its input and can prepare both historical rows with a target and prediction rows without `is_canceled`. `model_features()` returns only the approved predictor columns.

Focused tests are in [test_features.py](../tests/test_features.py). AUC comparisons and model training are intentionally deferred to the next phase.
