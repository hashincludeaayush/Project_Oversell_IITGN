# What would the client have asked a vendor for, in writing?

**Owner:** Client Lead. **Closes:** ladder stage 2. **Length:** one to two pages.

You write this request for proposal as the client would have issued it, so that both sides agree on what is being bought before anything is built. Vendor teams often draft the request with the client in B2B sales; treat that as the convention here. Keep the client's voice and the client's units: rooms, euros, walks.

### 1. What is the background, in three sentences?

> **Worked example.** Our home-collection unit runs about 300 routes a morning in three cities. Roughly one booked patient in seven is not home when the phlebotomist arrives, and each idle slot costs us about Rs 450. We overbook today by gut feel, route by route.

**Our answer:**
We are operating on two hotels in Portugal:
- City hotel in Lisbon
- Resort in the Algarve.

Roughly 37% of our bookings cancel before arrival, leaving rooms empty and forfeiting revenue that cannot be recovered on the day of stay. We currently manage this by overselling, but we are trying to get an automated, data-driven oversell policy that minimizes empty rooms without breaching our brand standard for walking guests.

<!-- answer:3 -->

### 2. What must the solution do?

_Five lines at most, each one a verb the client can check._

> **Worked example.** (1) Give the number of extra visits to book on each route for tomorrow morning. (2) Run on the bookings file we export at the end of each day. (3) Show the reason for each route's number in one line. (4) Report idle slots and turned-away patients for the past month. (5) Let the operations lead overrule a route and record why.

**Our answer:**
1. Return the recommended number of rooms to oversell for each of the next 14 arrival nights at each hotel.
2. Ingest our daily bookings export using only attributes known at booking time.
3. Provide a clear reason for each night's oversell recommendation.
4. Calculate the net financial cost (empty room loss + walked guest penalties) on our historical evaluation period.
5. Allow our revenue manager to review and overrule recommendations with an audit trail.
<!-- answer:5 -->

### 3. How good must it be, and on which period?

_Acceptance thresholds in business units, with the period each is measured on._

> **Worked example.** On the last three months of bookings, held back until the end: idle slots per route-morning at least 25% below today's gut-feel rule, with at most 5 patients turned away per 1,000 completed visits.

**Our answer:**
Proposals must demonstrate a reduction in total financial loss compared to our current flat rule over our proof period (arrivals from 1 January 2017 to 31 August 2017). Across that period, the rule must strictly maintain a walk rate of no more than 10 walked guests per 1,000 arrivals (at most 1.0%).
<!-- answer:3 -->

### 4. Within which limits and rules?

> **Worked example.** Use only what is known when the route is fixed. Patient data stays in our systems. The run takes under five minutes on a laptop. A route lead can read the reason for any number.

**Our answer:**
The model must rely strictly on data available at the time of booking. Recommendations must run in under five minutes on standard office hardware. Guest's privacy must be preserved with no export of identifiable customer data off premise.
<!-- answer:3 -->

### 5. What data do we provide?

> **Worked example.** Eighteen months of visit bookings, one row per booking, with the booking channel, slot, pincode, payment type, test panel and outcome.

**Our answer:**
A dataset of 119,390 historical bookings covering arrivals from July 2015 to August 2017 across 32 fields, including booking channels, lead times, deposit terms, customer segment, ADR, and final reservation status.
<!-- answer:2 -->

### 6. How will we judge proposals?

> **Worked example.** On the acceptance thresholds above, then on how clearly the vendor explains a wrong call, then on the cost to run.

**Our answer:**
- First, by whether the solution strictly honors our walk ceiling of 
<= 10 walks per 1,000 arrivals on the 2017 proof period. 
- Second, by total net Euro savings achieved over our current flat policy as calculated by our evaluation contract given in `src/contract.py`. 
- Third, by transparency and ease of morning operational use by our revenue manager.
<!-- answer:2 -->

### 7. What is the timeline?

> **Worked example.** A proof of concept in one week, a pilot on one city for a month, then a decision.

**Our answer:**
A proof of concept comparing candidate methods within one week, followed by delivery of a working nightly recommendation script and a 14-night deployment simulation by Friday.
<!-- answer:2 -->

### 8. What may the vendor ask us?

> **Worked example.** How each outcome is recorded and by whom; which routes changed shape during the period; what a turned-away patient costs beyond the voucher.

**Our answer:**
Clarification on the commercial terms of "Non-Refundable" group tour operator bookings; details on physical room capacities and seasonal closures; and our historical tolerance for overbooking during major city events.
<!-- answer:3 -->

### 9. What is on the wish list?

_Copy the client's wish-list item exactly. Your answer to it belongs in the PRD, not here._

**Our answer:**
<!-- answer:1 -->
