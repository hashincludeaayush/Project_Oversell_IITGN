# Grill Run 2 — PRD and Build Plan

**Date:** 14 November 2026
**Role:** Build Lead
**Tool:** ChatGPT
**Artifact:** `docs/PRD.md` and `docs/BUILD_PLAN.md`
**Purpose:** Challenge the PRD and Build Plan, identify weaknesses, and improve project documentation.

## Chat link

[https://chatgpt.com/share/6af8a341-d4ac-83e8-8986-5dea278ff012](https://chatgpt.com/share/6af8a341-d4ac-83e8-8986-5dea278ff012)

## Full conversation transcript
1. no i will ask and confirm model lead first
2. all those questions which you have mentioned
3. we need cancellation probabilities because it gives a wide range spectrum of idea about what range could cancel or not rather than binary predictions
4. a good model file should run everywhere if it is failing while running nightly workflow that means somethiong needs to be corrected so we will both sit together and look at where should we correct our code

Good. Your answers show that you understand the coordination required between the Model Lead and Build Lead.
Evaluation of Question 4
1. Should you start integration using assumptions?
Correct
No. You should confirm the model interface before writing integration code. Otherwise, you risk building nightly.py around an incorrect assumption.

2. What information should you request?
Correct
You identified all the required questions. Let's organize them into an integration agreement:
Requirement	What to confirm
Model artifact	Exact filename and location
Loading	How to load the saved model
Input	Required feature names, order and data types
Prediction	Exact method, such as predict_proba()
Output	Probability format and positive-class meaning
Buffer	Frozen buffer value or methodology for each hotel
Dependencies	Required Python packages and versions

3. Why probabilities rather than binary predictions?
Correct, with refinement
Probabilities provide more information than a simple yes/no prediction.

For example:
Booking	Cancellation probability
A	0.90
B	0.70
C	0.35
D	0.10

Expected cancellations can be estimated by summing the probabilities:
\[
E(\text{cancellations})=\sum_{i=1}^{n}p_i
\]

Here:
\[
0.90+0.70+0.35+0.10=2.05
\]

The expected cancellations are approximately 2.05, rather than simply counting binary predictions.

4. What if the model works on the Model Lead's computer but fails in your workflow?
Correct**

Working together is the right approach. But as Build Lead, you should also investigate:
- Missing dependencies.
- Different Python environments.
- Incorrect file paths.
- Feature-name or feature-order mismatches.
- Incompatible model serialization versions.
- Incorrect input or output formats.
The complete Grill Run 2 conversation is available through the shared ChatGPT link above. The conversation covered the following questions and follow-ups:

### 1. Historical data availability and the 14-day decision

**Challenge:** Can the system make a recommendation 14 days before arrival if the historical dataset contains only final booking information?

**Discussion and outcome:**
- A genuine 14-day-ahead simulation requires knowing which bookings existed at the decision date.
- Final historical booking records alone do not establish what was known 14 days before arrival.
- Historical booking snapshots or timestamped booking records are needed to reproduce the decision-time view.
- The PRD was clarified to acknowledge this limitation and avoid making unsupported claims.

### 2. Definition of bookings on the books

**Challenge:** Should only paid or partially paid reservations count as bookings on the books?

**Initial understanding:** Only paid or partially paid reservations should be included.

**Correction and outcome:**
- All valid reservations existing at the decision date should count, irrespective of payment status.
- Reservations created after the decision date must not be included.
- The PRD was clarified accordingly.

### 3. Expected cancellations, safety buffer and recommended oversell

**Challenge:** How should expected cancellations, the safety buffer and the recommended oversell be distinguished?

**Example discussed:**
- Expected cancellations: 8
- Safety buffer: 3
- Recommended oversell: 5

**Outcome:**
- Expected cancellations are the model's estimate.
- The safety buffer is a separate risk-control decision.
- Recommended oversell is calculated after accounting for the buffer.
- The Model Lead owns the model and buffer-selection logic; the Build Lead integrates the agreed output into the nightly workflow.

### 4. Model integration requirements

**Challenge:** What information is needed from the Model Lead before implementing the nightly workflow?

**Outcome:**
- Confirm the model artifact filename and location.
- Confirm the prediction interface and expected input format.
- Confirm whether predictions are probabilities or binary outputs.
- Confirm the frozen buffer and hotel-specific settings.
- Coordinate with the Model Lead if integration or prediction failures occur.

## Outcome

The grilling identified documentation and integration requirements concerning decision-time data availability, booking definitions, oversell calculations and model interfaces.

The accepted recommendations were incorporated into the PRD and Build Plan.

## Documents changed

- `docs/PRD.md`
- `docs/BUILD_PLAN.md`
- `docs/grill_02_prd.md`

**Commit containing these documentation changes:** `11f56df`

## Limitations

This file records the questions, answers and outcomes from the grilling. The shared ChatGPT conversation is provided above for reference. It does not claim that uncompleted validation scenarios or tests were conducted.
