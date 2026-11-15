# Correlation and Multicollinearity Analysis

**Owner:** Data Lead  
**Date:** 2026-11-15  
**Scope:** Approved model inputs used by the selected classifier

## Objective

Check whether relationships among approved predictors could make the model
unstable, obscure interpretation, or create redundant information. This audit
is separate from the timing audit: correlation does not make a field valid if
the field is learned after the booking outcome.

## Numeric analysis

Spearman correlations were calculated for the 11 numeric features used by the
selected classifier. Numeric variance inflation factors (VIFs) were calculated
with an intercept after standardizing the numeric matrix.

| Pair or feature | Result |
|---|---:|
| `is_repeated_guest` and `previous_bookings_not_canceled` | Spearman 0.757 |
| `stays_in_weekend_nights` and `stays_in_week_nights` | Spearman 0.238 |
| `lead_time` and `stays_in_week_nights` | Spearman 0.296 |
| Maximum numeric VIF (`stays_in_week_nights`) | 1.366 |
| `is_repeated_guest` VIF | 1.246 |
| `previous_bookings_not_canceled` VIF | 1.238 |

No numeric pair reached the high-correlation screening threshold of absolute
Spearman correlation 0.80. All numeric VIFs were below 1.4, well below the
common screening levels of 5 or 10.

## Categorical association analysis

Bias-corrected Cramer's V was calculated for pairs of categorical model
features. The strongest associations were:

| Pair | Cramer's V |
|---|---:|
| `hotel` and `agent` | 0.878 |
| `distribution_channel` and `agent` | 0.714 |
| `market_segment` and `distribution_channel` | 0.692 |
| `market_segment` and `agent` | 0.627 |
| `market_segment` and `company` | 0.547 |

These associations indicate overlapping booking-channel and partner
information. They are not evidence of target leakage. The fields remain
booking-time inputs under `docs/COLUMNS.md`, although their individual
importance should not be interpreted as independent causal effects.

## Decision

No approved model feature is removed based on this audit. The selected Random
Forest is less sensitive to coefficient instability than Logistic Regression,
and the numeric VIF results do not indicate severe multicollinearity. Keep the
22-feature Model Lead interface unchanged.

The Model Lead must still:

1. Use business cost and the walk-rate ceiling—not correlation alone—to assess
   sensitivity.
2. Report any feature-interface change before the Build Lead saves the model.

## Choose-period sensitivity check

The selected Random Forest configuration was refit on Train and evaluated on
Choose after removing the strongest numeric association's features
individually and together. Every variant found a compliant buffer, but every
variant had lower AUC than the frozen 22-feature policy.

| Interface | Features | Buffer | AUC | Choose cost (EUR) | Walks per 1,000 |
|---|---:|---:|---:|---:|---:|
| Full approved interface | 22 | 3 | 0.821727 | 1,384,174.34 | 8.150 |
| Remove `is_repeated_guest` | 21 | 2 | 0.818008 | 1,237,839.13 | 9.700 |
| Remove `previous_bookings_not_canceled` | 21 | 3 | 0.812862 | 1,367,780.58 | 7.770 |
| Remove both | 20 | 3 | 0.802092 | 1,411,886.41 | 8.740 |

The single-feature variants show that lower Choose cost alone would select a
different policy from the agreed highest-compliant-AUC rule. The full
22-feature interface is therefore retained, and the saved policy remains
unchanged. This sensitivity check does not use Proof data.

The categorical associations should be considered when explaining feature
importance. They do not authorize use of `agent`, `company`, or any other
post-booking field outside the approved timing bins.
