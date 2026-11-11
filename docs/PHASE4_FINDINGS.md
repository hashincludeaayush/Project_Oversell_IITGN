# Phase 4 findings: client claim checks

**Date:** 2026-11-11  
**Analyst:** Aayush Singh, Data Lead  
**Notebook:** [02_check_client_claims.ipynb](../notebooks/02_check_client_claims.ipynb)

## Findings

| Brief observation or number | Evidence from the raw data | Conclusion |
|---|---|---|
| About one booking in four is cancelled | 44,224 of 119,390 bookings are cancelled: **37.04%** overall. City Hotel is **41.73%** (33,102/79,330); Resort Hotel is **27.76%** (11,122/40,060). | The group-level statement is directionally about cancellations but understates the observed overall rate. Hotel-specific behavior must be retained. |
| Most prepaid/non-refundable bookings do not cancel | `Non Refund`: 14,494 of 14,587 cancelled: **99.36%**. `No Deposit`: **28.38%**. `Refundable`: **22.22%**. | The observation is contradicted by this dataset. Non-refundable bookings are not guaranteed outcomes here. |
| Vendor cancellation list was stopped by front desk | No vendor predictions, timestamps, or front-desk usage records are included. | Not verifiable from this dataset. |
| Vendor demo showed 95% accuracy | No vendor prediction file or evaluation record is included. | Not verifiable. Also, the client contract evaluates cost and walks, not accuracy alone. |
| Dataset size and period | 119,390 rows, 32 source columns, arrival dates 2015-07-01 through 2017-08-31. | Confirmed. |
| EUR 300 walk cost and 10 walks per 1,000 ceiling | These are policy inputs in the brief and `src/contract.py`, not fields measured in the bookings file. | Keep fixed in evaluation; do not estimate them from the data. |

## Scope decision

Market-segment and customer-type cancellation rates are shown in the notebook as descriptive evidence for the hidden-guest-types wishlist. No clustering or new guest-type feature is created in Phase 4. Feature timing and approved model inputs belong to the next phase.
