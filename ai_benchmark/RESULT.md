# Reconstructed AI Benchmark Results

**Status:** newly created/reconstructed benchmark. The historical
`ai-benchmark` branch was unavailable, so these are not historical AI results.

## Command and execution

Command:

```text
python ai_benchmark\run.py
```

The command completed successfully and wrote
`ai_benchmark/oversell_2017-08-18_31.csv`.

## Method and controls

- Data: 119,390 rows from the local `data/hotels.csv`.
- Split: Train 49,157; Choose 29,546; Proof 40,687.
- Dates: Train before 2016-07-01; Choose 2016-07-01 through 2016-12-31;
  Proof 2017-01-01 through 2017-08-31.
- Predictors: 23 fixed-at-booking columns from `docs/COLUMNS.md`; no target,
  status fields, amendable fields, or final ADR.
- Model: independent logistic regression with median-imputed/scaled numeric
  features and one-hot categorical features.
- Policy: `max(round(nightly expected cancellations - buffer), 0)`.
- Buffer search: integer buffers 0--30, selected on Choose only subject to
  the contract ceiling, then frozen for Proof.
- Baseline: hotel's Train cancellation rate times nightly bookings; its safety
  margin was separately selected on Choose under the same ceiling.

## Actual output

```text
RECONSTRUCTED AI BENCHMARK (new; not historical AI results)
rows=119390, train=49157, choose=29546, proof=40687, proof_dates=2017-01-01..2017-08-31
features=23 fixed-at-booking; model=logistic_regression
CHOOSE model: buffer=0, auc=0.817241, cost_eur=1736944.54, empty_rooms=4440, walked_guests=29, walks_per_1000=1.55, ceiling_met=True, nights=368
CHOOSE flat: buffer=16, auc=0.557317, cost_eur=2387929.64, empty_rooms=5442, walked_guests=185, walks_per_1000=9.92, ceiling_met=True, nights=368
PROOF model: auc=0.818367, cost_eur=2890485.30, empty_rooms=5884, walked_guests=71, walks_per_1000=2.85, ceiling_met=True, nights=486
PROOF flat: cost_eur=3882929.54, empty_rooms=8050, walked_guests=167, walks_per_1000=6.70, ceiling_met=True, nights=486, savings_eur=992444.24
```

The reconstructed model therefore saved **EUR 992,444.24** versus the
required flat reference on Proof, while both policies met the 10 walks per
1,000 ceiling.

## 14-night output

The complete table is in `oversell_2017-08-18_31.csv`. The frozen model buffer
is 0 for every row:

```text
hotel,arrival_date,book,expected,buffer,oversell
City Hotel,2017-08-18,121,16.878498,0,17
Resort Hotel,2017-08-18,60,4.842212,0,5
City Hotel,2017-08-19,122,35.354044,0,35
Resort Hotel,2017-08-19,66,9.348807,0,9
City Hotel,2017-08-20,101,13.448645,0,13
Resort Hotel,2017-08-20,58,10.385314,0,10
City Hotel,2017-08-21,94,13.724398,0,14
Resort Hotel,2017-08-21,65,9.569407,0,10
City Hotel,2017-08-22,60,7.094656,0,7
Resort Hotel,2017-08-22,38,2.993328,0,3
City Hotel,2017-08-23,86,9.112648,0,9
Resort Hotel,2017-08-23,40,3.307590,0,3
City Hotel,2017-08-24,91,11.839901,0,12
Resort Hotel,2017-08-24,65,14.370364,0,14
City Hotel,2017-08-25,139,16.896599,0,17
Resort Hotel,2017-08-25,52,4.622812,0,5
City Hotel,2017-08-26,101,20.490569,0,20
Resort Hotel,2017-08-26,65,9.609241,0,10
City Hotel,2017-08-27,107,15.718781,0,16
Resort Hotel,2017-08-27,67,6.887087,0,7
City Hotel,2017-08-28,133,56.018742,0,56
Resort Hotel,2017-08-28,78,8.030709,0,8
City Hotel,2017-08-29,90,22.011810,0,22
Resort Hotel,2017-08-29,35,2.449227,0,2
City Hotel,2017-08-30,47,6.598157,0,7
Resort Hotel,2017-08-30,42,3.760409,0,4
City Hotel,2017-08-31,79,11.921893,0,12
Resort Hotel,2017-08-31,55,2.520046,0,3
```

## Limitations

The export is a final-book dataset, not a historical T-14 snapshot, so the
14-night table is not evidence that these bookings were known fourteen days
before arrival. This benchmark uses one simple model and a bounded buffer
search; it is a reproducible challenger, not a replacement for the production
pipeline or a claim about the unavailable historical AI branch.
