# What did we decide, and why?

Two tables. The first is the Week 1 decisions log for the data: every cleaning or filtering choice, its reason and how many rows it touched. The second records team decisions and objections under the rule in `docs/ROLES.md`. Add rows; never delete them.

## Which data decisions did we make?

**Owner:** Data Lead.

| Date | Decision | Reason, with the number that justified it | Rows touched | Logged by |
|---|---|---|---|---|
| 2026-11-11 | Record Phase 4 claim checks before cleaning or feature selection | The raw file contains 119,390 rows and 32 source columns. The overall cancellation rate is 44,224/119,390 = 37.04%; rates differ by hotel: City Hotel 41.73% and Resort Hotel 27.76%. | 119,390 profiled; no rows changed | Aayush Singh |
| 2026-11-11 | Challenge the “non-refundable means guaranteed” observation | `Non Refund` contains 14,587 bookings, of which 14,494 are cancelled (99.36%). The result contradicts the client observation and must be explained in the charter; it is not a cleaning rule. | 14,587 `Non Refund` rows inspected; no rows changed | Aayush Singh |
| 2026-11-11 | Do not claim to verify the vendor’s operational or 95%-accuracy observations | The supplied dataset contains no vendor predictions, prediction timestamps, accuracy record, or front-desk usage records. These claims cannot be measured from this file. | 119,390 rows checked for available evidence; no rows changed | Aayush Singh |
| 2026-11-11 | Defer hidden guest-type discovery to a later analysis | Market-segment and customer-type cancellation rates were summarized descriptively, but no clustering or new feature was created in Phase 4. The MVP scope remains cancellation-aware nightly overbooking. | 119,390 rows summarized; no rows changed | Aayush Singh |
| 2026-11-11 | Fill missing `children` values with zero in the prepared feature view | Only 4 of 119,390 rows are missing `children`; it is a non-negative guest count. The raw export remains unchanged. | 4 prepared rows | Aayush Singh |
| 2026-11-11 | Represent missing `country` as `Unknown` in the prepared feature view | 488 rows have no country value. A separate category preserves the fact that the value was unknown instead of inventing a country. The raw export remains unchanged. | 488 prepared rows | Aayush Singh |
| 2026-11-11 | Represent missing `agent` and `company` as explicit no-partner categories | 16,340 rows have no agent and 112,593 have no company; `docs/DOMAIN.md` defines empty values as booked without one. The raw export remains unchanged. | 128,933 prepared cells | Aayush Singh |
| 2026-11-11 | Do not remove exact duplicates | The raw file contains 31,994 exact duplicate rows (40,165 rows in duplicate groups). `src/data.py` requires the export to remain exact, and the scoring unit is each booking row; deduplication would change the client's data. | 31,994 duplicate rows inspected; 0 removed | Aayush Singh |
| 2026-11-11 | Retain zero-night and anomalous ADR rows in the raw/scoring view | There are 715 zero-night rows, 1,959 zero-ADR rows, and 1 negative-ADR row. No row is removed before the contract evaluation; these values are flagged for later model review, while `adr` is not an MVP predictor in the Phase 5 audit. | 2,675 rows inspected; 0 removed | Aayush Singh |

## Which team decisions and objections did we log?

**Owner:** whoever made the decision. An objection is three lines: what I object to, why, what I propose.

| Date | Artifact | Decision or objection | Raised by | Answer, within 15 minutes | Settled by |
|---|---|---|---|---|---|
| | | | | | |
