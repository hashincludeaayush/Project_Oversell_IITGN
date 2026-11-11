# Phase 5 findings: column timing audit

**Date:** 2026-11-11  
**Analyst:** Aayush Singh, Data Lead  
**Notebook:** [03_audit_column_timing.ipynb](../notebooks/03_audit_column_timing.ipynb)

## Audit result

| Bin | Meaning | Count | MVP treatment |
|---:|---|---:|---|
| 1 | Fixed at booking | 23 | Eligible for MVP input after cleaning decisions are documented |
| 2 | Amendable or partly known at booking | 6 | Not used by default; requires an explicit caveat and comparison |
| 3 | After the fact | 3 | Never a model predictor |

The three Bin 3 columns are `is_canceled`, `reservation_status`, and `reservation_status_date`. `is_canceled` is the target; the other two describe final outcomes and would leak future information.

## Important boundary decisions

- `agent` and `company` are Bin 1. An empty value is treated as the meaningful “without one” category, consistent with [DOMAIN.md](DOMAIN.md).
- `assigned_room_type`, `booking_changes`, `days_in_waiting_list`, `adr`, `required_car_parking_spaces`, and `total_of_special_requests` are Bin 2 because they can be amended, accumulate, or become final only after time has passed.
- The AUC comparison table in [COLUMNS.md](COLUMNS.md) is intentionally still blank. It belongs to the modeling phase, not this timing audit.
