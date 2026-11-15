# Reconstructed AI benchmark execution record

**Date:** 16 November 2026  
**Role:** Data Lead  
**Tool:** Copilot delegated implementation agent  
**Artifacts:** `ai_benchmark/PLAN_AI.md`, `ai_benchmark/run.py`,
`ai_benchmark/RESULT.md`

## Status

This is an execution record for a newly created reconstructed benchmark. It is
not the missing historical `ai-benchmark` branch or a pasted historical chat
transcript.

## Command

```text
python ai_benchmark\run.py
```

## Recorded result

- Independent model: Logistic Regression
- Features: 23 fixed-at-booking columns
- Choose buffer: 0
- Choose AUC: 0.817241
- Proof AUC: 0.818367
- Proof model cost: EUR 2,890,485.30
- Proof flat-rule cost: EUR 3,882,929.54
- Proof savings: EUR 992,444.24
- Proof empty rooms: 5,884
- Proof walked guests: 71
- Proof walks per 1,000: 2.85
- Walk ceiling: met

The command completed successfully, wrote the 14-night benchmark table, and
the repository test suite reported 58 passing tests. The final-book/T-14
limitation is documented in `ai_benchmark/RESULT.md`.
