# Reconstructed AI Benchmark Plan

This is a newly created/reconstructed benchmark. The historical `ai-benchmark`
branch and its recorded AI output are not available in this checkout, so these
artifacts do not claim to be historical AI results.

## Objective

Estimate each scored booking's probability of cancellation and aggregate those
probabilities to one non-negative whole-room oversell count per hotel and
arrival night. The client contract in `src/contract.py` is the scoring
authority and will not be modified.

## Data and split

- Read `data/hotels.csv`, without downloading another dataset.
- Parse the three arrival-date columns into `arrival_date`.
- Train: arrivals before `2016-07-01`.
- Choose: arrivals from `2016-07-01` through `2016-12-31`.
- Proof: arrivals from `2017-01-01` through `2017-08-31`.
- Fit the model on Train only. Select the integer buffer on Choose, then freeze
  it before evaluating Proof.

## Predictors

Use only fixed-at-booking columns from `docs/COLUMNS.md`: `hotel`,
`lead_time`, arrival-date components, requested stay length, guest counts,
`meal`, `country`, `market_segment`, `distribution_channel`,
`is_repeated_guest`, prior cancellation/history counts, `reserved_room_type`,
`deposit_type`, `agent`, `company`, and `customer_type`.

Do not use `is_canceled`, `reservation_status`,
`reservation_status_date`, or amendable fields such as final ADR,
`assigned_room_type`, and running request/change counts as predictors.
Missing children, country, agent, and company values receive explicit
booking-time-safe values.

## Model and policy

- Model: a scikit-learn logistic-regression probability model with one-hot
  categorical values, median-imputed/scaled numeric values, and
  `handle_unknown="ignore"` for unseen categories.
- The target is `is_canceled`.
- For each candidate buffer from 0 through 30 rooms, compute
  `k = max(round(sum(probabilities for the night) - buffer), 0)`.
- Choose the least-cost candidate on Choose among policies at or below the
  contract's 10 walks per 1,000 arrivals ceiling. Freeze that buffer.
- Apply the frozen model and buffer once to Proof.

## Required baseline and reporting

The required flat baseline uses each hotel's Train cancellation rate times the
night's bookings. Its fixed safety margin is selected independently on Choose
using the same 0--30 search and walk ceiling, then frozen for Proof.

For both model and baseline, report contract metrics in euros, empty rooms,
walked guests, walks per 1,000, ceiling status, and number of nights for
Choose and Proof. Also report the model's Choose/Proof AUC and the requested
14-night oversell table for 2017-08-18 through 2017-08-31.

## Limitations

This is a final-book export, not a historical snapshot of what was known
fourteen days before each arrival. The benchmark therefore cannot prove a
real-time T-14 workflow. It also uses a simple logistic model and a fixed
buffer search rather than tuning a broader model family.
