# What is the project, in one page?

**Owner:** Client Lead. **Closes:** ladder stages 0 and 1. **Length:** one page. **Version 0** is written on paper on Tuesday, with no AI, and typed in here before any AI tool is opened.

Answer each question in one to three sentences. The worked example comes from a different business on purpose (home sample collection at a diagnostics chain, with made-up numbers), so it shows the standard of an answer without giving you the hotel's.

### 1. Who is the client, and who pays whom?

> **Worked example.** The client is the home-collection unit of a diagnostics chain. Patients pay per test (B2C); partner hospitals and corporate health camps pay on monthly invoices (B2B). We are the analytics vendor, and the unit head renews us only if idle phlebotomist slots fall.

**Our answer:**
Our client is the Director of Revenue for a two-hotel group in Portugal 
1. City Hotel in Lisbon
2. Resort Hotel in the Algarve

Guests pay the hotel directly or via travel agents for stays. The hotel group engages RateGain as their revenue-science squad, and the engagement renews only if net revenue increases by cutting empty room losses while staying within the walk limits.

<!-- answer:3 -->

### 2. Who decides, how often, and what does one wrong call cost in each direction?

> **Worked example.** The city operations lead fixes each route's bookings every evening for the next morning. An empty slot costs about Rs 450 of phlebotomist time and fuel. A patient we cannot reach in time costs about Rs 600 in a voucher and a rebooking, plus a complaint.

**Our answer:**
The hotel revenue manager decides every morning how many extra rooms beyond capacity to oversell for each of the next 14 arrival nights.

<!-- answer:3 -->

### 3. What is decided, from what is known when, about which outcome?

> **Worked example.** How many extra visits to book on each route for tomorrow morning, from the bookings known at the end of today, about how many booked patients will not be there when the phlebotomist arrives.

**Our answer:**

<!-- answer:3 -->

### 4. What is the unit of decision, and why that unit?

> **Worked example.** The route-morning: one phlebotomist, one morning, about 12 slots. The overbooking is set per route, so per-patient answers are only useful once they are added up per route.

**Our answer:**

<!-- answer:2 -->

### 5. What are the north star and the guardrail?

_Give each one a numerator, a denominator, a window and the exclusions. Draw the metric tree underneath: the north star at the top, the two costs below it, the guardrail beside it._

> **Worked example.** North star: idle slots per route-morning, averaged over a calendar month, excluding routes the lab cancelled. Guardrail: patients turned away per 1,000 completed visits, per calendar month, all routes, at most 5.

**Our answer:**

<!-- answer:4 -->

### 6. Which numbers in the brief did we check, and what did the data say?

_Every number in the brief gets a row. A number you could not check gets a question to the client instead._

> **Worked example.**
>
> | Number in the brief | What we checked | What the data said | What we do about it |
> |---|---|---|---|
> | "A home visit takes 20 minutes" | Median time from arrival to sample scan | 26 minutes; 20 is the planned slot length | Plan on the record, not the plan |

| Number in the brief | What we checked | What the data said | What we do about it |
|---|---|---|---|
| "About one booking in four is cancelled" | `is_canceled` across all 119,390 bookings and by hotel | 44,224 cancellations, or 37.04% overall; City Hotel 41.73% (33,102/79,330); Resort Hotel 27.76% (11,122/40,060) | Do not hard-code 25% for the group. Estimate cancellation behavior by hotel and evaluate the flat baseline against the same proof period. |
| "Most prepaid, non-refundable bookings never turn into a stay" | Cancellation rate by `deposit_type` | `Non Refund`: 14,494/14,587 cancelled (99.36%); `No Deposit`: 29,694/104,641 (28.38%); `Refundable`: 36/162 (22.22%) | The observation is contradicted by this dataset. Treat `deposit_type` as an important candidate input, subject to the timing audit; do not describe non-refundable bookings as guaranteed. |
| "A vendor list was stopped by the front desk" | Checked whether the supplied rows contain vendor predictions, timestamps, or usage records | No vendor prediction or front-desk usage fields are present | Cannot verify this historical claim from the supplied data. Evaluate our rule at the hotel-night level using the supplied contract instead. |
| "A vendor demo showed 95% accuracy" | Checked whether the supplied rows contain the demo predictions or an evaluation definition | No demo predictions or accuracy record are present; the client contract scores euros, rooms, and walks per 1,000 instead | Cannot verify the 95% figure. Do not use accuracy as the acceptance criterion; report the contract metrics. |
| "119,390 bookings from July 2015 to August 2017" | Raw row count, source-column count, and constructed arrival dates | 119,390 rows, 32 source columns, arrival dates 2015-07-01 to 2017-08-31 | Keep the raw loader unchanged and use the stated chronological train/choose/proof split. |
| "EUR 300 per walked guest" and "at most 10 walks per 1,000" | Compared policy values with raw booking data | These are client/course policy inputs, not values estimable from booking rows | Keep them as fixed contract constants and reject any rule exceeding the walk ceiling. |
| About one booking in four is cancelled|  checked `is_cancelled` rate across 119,390 bookings, also broken down by hotel | Total 44,224 bookings cancelled: 37.04% overall. **City Hotel:** (41.73%) **Resort Hotel:** (27.76%) | |

### 7. What is out of scope?

> **Worked example.** Pricing of home visits, phlebotomist hiring, and routes outside the three metro cities.

**Our answer:**

<!-- answer:2 -->

### 8. Who owns what on this team?

| Role | Name | Owns |
|---|---|---|
| Client Lead | Chaitanya and Harsh | |
| Data Lead | Rishabh and Aayush | |
| Model Lead | Chaitanya and Harsh | |
| Build Lead | Rishabh and Aayush | |

### 9. What is the one question we are sending the client?

> **Worked example.** "Is a no-show recorded by the phlebotomist at the door, or by the call centre the next day?"

**Our answer:**

<!-- answer:2 -->
