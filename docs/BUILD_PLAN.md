# Build Plan
## Project Oversell – Hotel Overbooking Recommendation System

**Owner:** Build Lead  
**Project:** IIT Gandhinagar – Week 6 Build  
**Objective:** Build, test and deliver a working hotel overbooking recommendation pipeline.

---

## 1. Build phases

| Phase | Deliverable | Owner | Planned hours | Actual hours | Done when | Evidence |
|---|---|---|---:|---:|---|---|
| POC | Data preparation and feature pipeline | Data Lead | 4 | To be updated | Approved booking-time features are prepared correctly | `src/features.py`, `docs/COLUMNS.md` |
| POC | Candidate model and baseline comparison | Model Lead | 6 | To be updated | Candidate methods are evaluated using the agreed business metric | `src/backtest.py`, `docs/COMPARISON.md` |
| POC | Business-cost and walk-rate validation | Model Lead | 3 | To be updated | Empty rooms, walked guests, cost and walk rate are calculated using the contract | Backtest output |
| MVP | Nightly recommendation pipeline | Build Lead | 6 | To be updated | The script generates recommendations for the requested hotel-arrival nights | `src/nightly.py` |
| MVP | Model integration | Build Lead and Model Lead | 3 | To be updated | Nightly pipeline successfully loads the selected model and frozen settings | Integration test |
| MVP | Output validation | Build Lead | 1 | To be updated | Output contains all required columns and valid recommendations | Generated output file |
| Final | Proof-period evaluation review | Model Lead | 2 | To be updated | Frozen method is evaluated on proof without further tuning | Backtest results |
| Final | Uncertainty buffer review | Model Lead and Build Lead | 2 | To be updated | Buffer approach is compared and documented | Comparison results |
| Final | Full-night caveat and roadmap | Build Lead and Client Lead | 2 | To be updated | Final-book limitation and future improvements are documented | `docs/ROADMAP.md`, PRD |
| Final | Documentation and presentation | All team members | 3 | To be updated | Required documents and slides are complete and reviewed | Project documents and slides |

**Note:** Planned hours are initial estimates for team discussion, not committed actual effort. Actual hours must be updated from the team's time spent.

---

## 2. POC – Proof of Concept

**Objective:** Establish whether the available booking data can support a reliable overbooking recommendation.

### Tasks

1. Inspect the dataset and understand its structure.
2. Identify the booking-time columns that are safe to use.
3. Prepare the model features.
4. Train and compare candidate cancellation-prediction methods.
5. Establish the client flat-rule baseline.
6. Calculate empty rooms, walked guests and business cost.
7. Check the walk-rate guardrail.
8. Record the method comparison and supporting evidence.

### POC completion criteria

- Data preparation works correctly.
- No target leakage is present.
- Candidate methods are compared using the same evaluation contract.
- The client baseline is included.
- The train, choose and proof periods are kept separate.
- The walk-rate ceiling is checked.
- Results are documented with actual outputs.

### Evidence files

- `src/features.py`
- `src/backtest.py`
- `docs/COLUMNS.md`
- `docs/COMPARISON.md`
- `docs/DECISIONS.md`

---

## 3. MVP – Minimum Viable Product

**Objective:** Generate a usable 14-night overbooking recommendation table for the two hotels.

### Tasks

1. Create `src/nightly.py`.
2. Load the prepared booking data.
3. Load the selected model and frozen settings.
4. Generate cancellation probabilities.
5. Aggregate predictions by hotel and arrival date.
6. Calculate expected cancellations.
7. Apply the approved safety buffer.
8. Calculate the recommended oversell quantity.
9. Generate the output table.
10. Validate the output and run tests.

### Required output columns

| Column | Meaning |
|---|---|
| hotel | Hotel name |
| arrival_date | Arrival night |
| bookings_on_book | Number of bookings represented in the input |
| expected_cancellations | Sum of cancellation probabilities |
| buffer | Safety margin |
| recommended_oversell | Recommended oversell quantity |

### MVP completion criteria

- The nightly script executes successfully.
- The selected model is loaded correctly.
- The script generates one row per hotel and arrival night.
- The output covers the requested 14-night period.
- All output values are valid.
- The script does not modify `src/contract.py`.
- The output can be reproduced from the same inputs and saved model.

### Expected command

```powershell
python src/nightly.py --from 2017-08-18 --nights 14
```

The exact output filename and model-loading interface must match the implementation agreed with the Model Lead.

---

## 4. Final – Validation and delivery

**Objective:** Confirm that the MVP meets the project requirements and clearly communicate its limitations.

### Tasks

1. Run the frozen model on the proof period.
2. Compare the selected approach against the client baseline.
3. Confirm the walk-rate guardrail.
4. Review the uncertainty buffer.
5. Document the final-book versus 14-day-on-book limitation.
6. Complete the product roadmap.
7. Review the PRD and build plan.
8. Complete and validate presentation slides.
9. Run the complete test suite.

### Final completion criteria

- Proof-period results are available.
- No tuning has been performed using proof results.
- The final method is documented.
- The walk-rate ceiling is respected.
- The PRD contains actual evaluation results.
- The roadmap identifies production improvements.
- The required documents and presentation are ready.

---

## 5. Production roadmap items

These are possible extensions beyond the MVP. Estimates are provisional and should be agreed with the team.

| Production improvement | Purpose | Initial effort estimate |
|---|---|---:|
| Live booking-system integration | Retrieve current hotel bookings | 8 hours |
| Automated daily execution | Generate recommendations every morning | 5 hours |
| Revenue-manager dashboard | Display recommendations clearly | 10 hours |
| Model performance monitoring | Detect deterioration in prediction quality | 8 hours |
| Manual override and audit log | Allow managers to adjust recommendations and record reasons | 6 hours |
| High walk-risk alerts | Notify managers when a night approaches the walk-rate limit | 5 hours |
| As-of-date booking snapshots | Reproduce the information actually available at the 14-day decision point | 10 hours |

---

## 6. Scope priorities

| Priority | Feature | Decision |
|---|---|---|
| Must have | Data preparation | MVP requirement |
| Must have | Cancellation prediction | MVP requirement |
| Must have | Business-cost evaluation | MVP requirement |
| Must have | Walk-rate guardrail | MVP requirement |
| Must have | Nightly recommendation table | MVP requirement |
| Should have | Uncertainty buffer comparison | Final validation |
| Should have | Clear limitation documentation | Final delivery |
| Could have | Dashboard | Future production work |
| Could have | Live booking integration | Future production work |
| Could have | Automated alerts | Future production work |
| Out of scope | Automatic booking acceptance | Not part of MVP |
| Out of scope | Automatic guest relocation | Not part of MVP |

---

## 7. Testing and validation checklist

- [ ] `src/contract.py` remains unchanged.
- [ ] Feature preparation uses approved columns.
- [ ] `is_canceled` is used only as the prediction target.
- [ ] No post-booking information is used as a model predictor.
- [ ] Train, choose and proof periods are separated.
- [ ] The client baseline is included.
- [ ] The walk-rate ceiling is checked.
- [ ] The selected model and buffer are saved.
- [ ] The nightly pipeline loads the saved model correctly.
- [ ] The 14-night output contains all required columns.
- [ ] The generated output has valid values.
- [ ] `pytest -q` passes.
- [ ] The PRD and roadmap reflect actual project results.
- [ ] The challenger has reviewed and signed the relevant artifact.

---

## 8. Build Lead responsibilities

The Build Lead is responsible for:

1. Maintaining the project architecture and build plan.
2. Coordinating interfaces between feature preparation, model training and nightly prediction.
3. Developing and validating `src/nightly.py`.
4. Maintaining `AGENTS.md`.
5. Maintaining `docs/PRD.md` and `docs/ROADMAP.md`.
6. Tracking team dependencies and unresolved decisions.
7. Ensuring the implementation follows the evaluation contract.
8. Reviewing the final deliverables before submission.

**Important:** A document is not considered complete merely because it exists. It must be implemented or reviewed, tested where applicable, and supported by evidence.