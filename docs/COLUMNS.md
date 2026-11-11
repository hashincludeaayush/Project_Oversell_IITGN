# Which columns did the hotel know on the day of booking?

**Owner:** Data Lead. **Closes:** part of ladder stage 1. **Used by:** `src/features.py`, the PRD and slide 4.

Put every column in exactly one bin, by when the hotel learns its value:

1. **Fixed at booking**: known on the day the booking is made, and it does not change.
2. **Amendable**: known at booking but it can change before arrival, or it is only partly known at booking.
3. **After the fact**: written at check-in, during the stay, or when the outcome is already known.

Only the first bin feeds the MVP. A second-bin column may be tried with its caveat written beside it. A third-bin column never feeds a method. The dataset article (Antonio, de Almeida and Nunes, 2019) says how several columns were recorded; cite it where it settles a bin.

The evidence column holds the number or the source that settled the bin, for example a rate you computed, or a sentence from the dataset article.

| Column | Bin (1, 2 or 3) | Why | Evidence |
|---|---|---|---|
| `hotel` | 1 | Hotel is selected when the reservation is made. | Dataset field identifying the hotel; booking-time property. |
| `is_canceled` | 3 | Outcome being predicted; known only after cancellation/no-show handling. | `src/data.py` defines it as the outcome column. |
| `lead_time` | 1 | Days between booking and arrival; known when booking is made. | Dataset field definition. |
| `arrival_date_year` | 1 | Requested arrival year is part of the reservation request. | Dataset arrival-date field. |
| `arrival_date_month` | 1 | Requested arrival month is part of the reservation request. | Dataset arrival-date field. |
| `arrival_date_week_number` | 1 | Requested arrival week is derived from the arrival date. | Dataset arrival-date field. |
| `arrival_date_day_of_month` | 1 | Requested arrival day is part of the reservation request. | Dataset arrival-date field. |
| `stays_in_weekend_nights` | 1 | Requested weekend nights are part of the stay length. | Dataset stay-length field. |
| `stays_in_week_nights` | 1 | Requested weekday nights are part of the stay length. | Dataset stay-length field. |
| `adults` | 1 | Number of adults is supplied with the reservation. | Dataset guest-count field. |
| `children` | 1 | Requested number of children is supplied; blanks are a separate cleaning question. | Dataset guest-count field. |
| `babies` | 1 | Requested number of babies is supplied with the reservation. | Dataset guest-count field. |
| `meal` | 1 | Requested meal plan is part of the reservation. | Dataset reservation field. |
| `country` | 1 | Guest country of origin is recorded with the reservation. | Dataset guest-origin field. |
| `market_segment` | 1 | Customer segment is recorded for the booking. | Dataset booking-segment field. |
| `distribution_channel` | 1 | Channel through which the booking arrived is known at booking. | Dataset channel field. |
| `is_repeated_guest` | 1 | Recognised repeat-guest status comes from booking history. | Dataset repeat-guest field. |
| `previous_cancellations` | 1 | Prior cancellations are historical information available at booking. | Dataset booking-history field. |
| `previous_bookings_not_canceled` | 1 | Prior completed bookings are historical information available at booking. | Dataset booking-history field. |
| `reserved_room_type` | 1 | Requested/reserved room type is known at booking. | Dataset reservation field. |
| `assigned_room_type` | 2 | Assigned room can differ from reserved room and change before arrival. | Dataset distinguishes reserved and assigned room types. |
| `booking_changes` | 2 | Running count can increase after the original booking. | Dataset reservation-change field. |
| `deposit_type` | 1 | Deposit policy attached to booking is known when made. | Dataset deposit-policy field. |
| `agent` | 1 | Agent identifier, including no-agent as a category, is attached to booking. | `docs/DOMAIN.md`: empty means booked without one. |
| `company` | 1 | Company identifier, including no-company as a category, is attached to booking. | `docs/DOMAIN.md`: empty means booked without one. |
| `days_in_waiting_list` | 2 | Duration is known only after time has elapsed and may not be final at initial booking. | Dataset waiting-list field. |
| `customer_type` | 1 | Customer type is recorded as part of booking classification. | Dataset customer-type field. |
| `adr` | 2 | Rate may change through amendments; not treated as immutable at initial booking. | Dataset price field; amendments can alter final rate. |
| `required_car_parking_spaces` | 2 | Parking requirements can be added or changed before arrival. | Dataset request field. |
| `total_of_special_requests` | 2 | Special requests can accumulate or change before arrival. | Dataset request count. |
| `reservation_status` | 3 | Final reservation outcome, including cancellation or check-in status. | Dataset outcome-status field. |
| `reservation_status_date` | 3 | Date when final reservation status was set. | Dataset outcome-date field. |

## What happens to a method when the late columns go in?

_Train the same method twice on the same split, once with first-bin columns only and once with the second and third bins added. Then run the first version once more on a random split. Record the three AUCs here and say which one the client should believe._

| Run | Columns | Split | AUC on the proof period |
|---|---|---|---|
| A | First bin only | Time | |
| B | All three bins | Time | |
| C | First bin only | Random | |
