# Build Plan
## Project Oversell - Hotel Overbooking Recommendation System

**Owner:** Build Lead
**Project:** IIT Gandhinagar - Week 6 Build
**Objective:** Build, test and deliver a working hotel overbooking recommendation pipeline.
**Status:** Local MVP implementation and validation completed; fresh-checkout verification and final team sign-offs remain open.

---

## 1. Build phases

| Phase | Deliverable | Owner | Planned hours | Actual / retrospective estimate (hours) | Done when | Evidence |
|---|---|---|---:|---:|---|---|
| POC | Data preparation and feature pipeline | Data Lead | 4 | 3 (recorded) | Approved booking-time features are prepared correctly | `src/features.py`, `docs/COLUMNS.md` |
| POC | Leakage and AUC experiment | Data Lead | 3 | 4 (recorded) | Valid, leaked and random-split AUCs are compared and documented | `src/phase8_leakage_auc.py`, `notebooks/05_leakage_auc_experiment.ipynb`, `docs/PHASE8_FINDINGS.md` |
| POC | Exploratory data analysis and modeling hypotheses | Data Lead | 6 | 7 (recorded) | Cancellation patterns are explored and leakage-safe modeling hypotheses are documented | `notebooks/04_exploratory_insights.ipynb`, `docs/PHASE8_FINDINGS.md` |
| POC | Correlation and multicollinearity audit | Data Lead | 2 | Not recorded | Numeric correlation, VIF and categorical association are measured and documented without unapproved feature removal | `notebooks/06_correlation_multicollinearity.ipynb`, `docs/CORRELATION_ANALYSIS.md` |
| POC | Candidate model and baseline comparison | Model Lead | 6 | Not recorded | Candidate methods are evaluated using agreed business and model-selection metrics | `src/backtest.py`, `docs/COMPARISON.md` |
| POC | Business-cost and walk-rate validation | Model Lead | 3 | Not recorded | Empty rooms, walked guests, cost and walk rate are calculated using the contract | Backtest output |
| MVP | Nightly recommendation pipeline | Build Lead | 6 | 6 (estimated retrospectively) | Script generates recommendations for requested hotel-arrival nights | `src/nightly.py`, `output/nightly_recommendations.csv` |
| MVP | Model integration | Build Lead and Model Lead | 3 | 2 (estimated retrospectively) | Nightly pipeline loads selected model and frozen settings | `models/selected_policy.joblib`, persistence and prediction helpers, tests |
| MVP | Output validation | Build Lead | 1 | 4 (estimated retrospectively) | Output contains required columns and valid recommendations; tests pass | `output/nightly_recommendations.csv`, `tests/test_nightly.py`, test run |
| Final | Proof-period evaluation review | Model Lead | 2 | Not recorded | Frozen method is evaluated and caveat is documented | `docs/COMPARISON.md`, `docs/DECISIONS.md` |
| Final | Uncertainty buffer review | Model Lead and Build Lead | 2 | Included in integration estimate; not separately timed | Saved buffer and calculation are verified against implementation | `models/selected_policy.joblib`, `src/nightly.py`, tests |
| Final | Full-night caveat and roadmap | Build Lead and Client Lead | 2 | Included in documentation estimate; not separately timed | Final-book limitation and future improvements are documented | `docs/ROADMAP.md`, PRD |
| Final | Documentation and presentation | All team members | 3 | Build Lead documentation estimate: 3; presentation effort not recorded | Required documents and slides are complete and reviewed | Project documents and team presentation |

**Hours note:** The three Data Lead values marked “recorded” were already present in the team's plan. Build Lead values are retrospective estimates based on the implementation, debugging, test execution, Git checks and documentation work visible in the project conversation; they are not measured timesheet entries. Other team members' unrecorded hours have deliberately not been invented. “Included” means the work is counted in another estimate and is not added again.

### Build Lead retrospective effort estimate

| Work category | Estimated hours |
|---|---:|
| Architecture, requirements and build planning | 3 |
| Model integration coordination and verification | 2 |
| Nightly pipeline implementation and debugging | 6 |
| Tests, execution and output validation | 4 |
| PRD, Build Plan and documentation review | 3 |
| Git checks, debugging reports and final integration checks | 2 |
| **Estimated Build Lead effort to date** | **20** |

This is a reasoned estimate from the work evidenced in the conversation, not an exact time record. It excludes other team members' effort and unfinished presentation/fresh-checkout work.

---

## 2. POC - Proof of Concept

**Objective:** Establish whether the available booking data can support an overbooking recommendation.

### Tasks

1. Inspect the dataset and understand its structure.
2. Identify booking-time columns that are safe to use.
3. Prepare model features using the Data Lead's approved feature pipeline.
4. Train and compare candidate cancellation-prediction methods.
5. Establish the client flat-rule baseline.
6. Calculate empty rooms, walked guests and business cost.
7. Check the walk-rate guardrail.
8. Record the method comparison and supporting evidence.

### POC completion criteria

- [x] Data preparation and feature interface are available.
- [x] Leakage analysis and exploratory findings are documented.
- [x] Candidate methods and baseline comparison are documented in project evaluation evidence.
- [x] The client baseline is included in the reported comparison.
- [x] Train, Choose and Proof periods are documented.
- [x] The walk-rate ceiling is checked in the reported Choose and frozen Proof results.
- [x] Model-selection decisions and supporting evidence are recorded.
- [ ] The full correlation/multicollinearity audit and all associated sign-offs have not been independently re-verified as part of this Build Lead close-out.

### Evidence files

- `src/features.py`
- `src/backtest.py`
- `docs/COLUMNS.md`
- `docs/COMPARISON.md`
- `docs/DECISIONS.md`
- `docs/EVALUATION_CONTRACT.md`
- `docs/PHASE8_FINDINGS.md`

---

## 3. MVP - Minimum Viable Product

**Objective:** Generate a usable 14-night overbooking recommendation table for the two hotels.

### 3.1 Selected model and settings

The Model Lead selected the following machine-learning policy:

| Setting | Confirmed value |
|---|---|
| Model | Random Forest |
| Number of estimators | 100 |
| Maximum depth | 12 |
| Minimum samples per leaf | 20 |
| Choose-period AUC | 0.821727 |
| Choose-period MAE | 7.432268 |
| Choose-period walks per 1,000 arrivals | 8.15 |
| Choose-period cost | EUR 1,384,174.34 |
| Choose-period savings versus Flat Rule | EUR 1,003,755.30 |
| Logistic Regression Choose-period AUC | 0.8168 |
| Frozen global buffer | 3 rooms |

The selected Random Forest uses the 22-feature `FEATURE_COLUMNS` interface defined by the Model Lead in `src/models/classifiers.py`.

The Data Lead's `features.MODEL_FEATURES` interface contains 23 approved booking-time predictors. The selected Random Forest intentionally excludes `arrival_date_year` because Train contains 2015 and 2016, whereas Proof and intended later use contain 2017 onward. Seasonality is represented through arrival month and week number.

The saved model's feature list, order, types and preprocessing are persisted with the selected policy and used during nightly inference.

The Choose-period AUC is the model-selection result. It does not replace business-cost or walk-rate validation.

### 3.2 Model integration agreement - completed locally

The original integration questions have been resolved in the implementation:

1. **Selected model:** Random Forest with 100 estimators, maximum depth 12 and minimum samples per leaf 20.
2. **Selected features:** 22-feature `FEATURE_COLUMNS` interface; `arrival_date_year` is excluded.
3. **Saved artifact:** `models/selected_policy.joblib`.
4. **Serialization:** joblib.
5. **Loading interface:** `models.persistence.load_selected_policy()`.
6. **Prediction interface:** `models.helpers.predict_cancellation_probability()`.
7. **Positive class:** For binary `is_canceled`, probability column 1 represents `is_canceled = 1` (cancelled).
8. **Frozen settings:** Global buffer of 3 rooms, persisted in the selected policy.
9. **Buffer calculation:** `max(0, round(expected_cancellations - buffer))`, using the rounding behaviour in the implementation.
10. **Choose validation:** Selected Random Forest with buffer 3 reports 8.15 walks per 1,000 arrivals, below the ceiling of 10.
11. **Nightly behaviour:** Loads the saved artifact and does not retrain, refit preprocessing or retune the buffer.

The local integration and tests have been verified. Execution from a separate fresh checkout remains unverified and is still a delivery check.

### 3.3 Nightly recommendation pipeline

**File:** `src/nightly.py`
**Owner:** Build Lead

#### Implemented behaviour

1. Read the booking input data.
2. Prepare booking rows using `features.prepare_bookings(raw, require_target=False)`.
3. Load the selected saved policy from `models/selected_policy.joblib`.
4. Use the saved model pipeline and its persisted feature configuration.
5. Generate one cancellation probability per booking through the shared prediction helper.
6. Validate prediction count, finiteness and probability bounds [0, 1].
7. Preserve booking-row association before aggregation.
8. Aggregate booking counts and predicted cancellation probabilities by `hotel` and `arrival_date`.
9. Read the frozen global buffer from the saved policy.
10. Calculate the non-negative integer oversell recommendation.
11. Validate requested hotel/date coverage and output values.
12. Write the recommendation CSV.
13. Run unit/integration tests and validate the generated output.

The nightly script does not retrain the model, refit preprocessing, retune the buffer, select a different model, use actual cancellation outcomes to generate predictions or use post-booking outcome fields as predictors.

#### Required output columns

| Column | Meaning |
|---|---|
| `hotel` | Hotel name |
| `arrival_date` | Arrival night |
| `bookings_on_book` | Number of booking records included in the prediction input for that hotel and arrival night |
| `expected_cancellations` | Sum of cancellation probabilities for those bookings |
| `buffer` | Frozen global safety margin of 3 rooms |
| `recommended_oversell` | Recommended oversell quantity |

#### Implemented oversell calculation

`recommended_oversell = max(0, round(expected_cancellations - buffer))`

The saved buffer is used. The nightly script does not independently tune it or create hotel-specific values.

#### Verified local execution

Run from the project root in the activated project environment:

```powershell
& .\.venv\Scripts\python.exe src\nightly.py --from 2017-08-18 --nights 14
```

Verified result:

- 28 output rows.
- 14 arrival nights.
- Two hotels.
- Six required output columns.
- Buffer value 3 throughout the generated output.
- Valid finite probability aggregates and no negative oversell recommendations.
- Output written to `output/nightly_recommendations.csv`.
- Full test suite: **58 passed**.

The command uses the available final-book dataset. It is a verified local pipeline execution, not a genuine historical T-14 simulation. A separate fresh-checkout execution has not been verified.

#### MVP completion criteria

- [x] Nightly script executes successfully in the current project environment.
- [x] Selected Random Forest policy loads successfully.
- [x] Saved preprocessing pipeline is included in the artifact and used.
- [x] The selected model uses its persisted 22-feature interface.
- [x] `arrival_date_year` is excluded from the selected classifier.
- [x] Frozen global buffer of 3 rooms is loaded from the saved policy.
- [x] One finite cancellation probability in [0, 1] is produced per input booking.
- [x] Booking predictions are associated with their input rows before aggregation.
- [x] Output covers the requested 14-night period for both hotels in the verified run.
- [x] Output contains all six required columns.
- [x] Local output values were validated.
- [x] Nightly execution does not retrain or retune the model or buffer.
- [x] `src/contract.py` was not modified as part of the verified Build Lead changes.
- [x] Output is generated using the saved policy and current input data.
- [ ] Execution from a separate fresh checkout has not yet been verified.
- [ ] Genuine as-of-date/T-14 input reconstruction has not been implemented or validated.

### Important operational limitation

The available dataset represents final booking information and does not automatically provide historical booking snapshots.

A genuine 14-day-ahead recommendation requires only bookings that existed on or before the simulated decision date. Unless historical booking-time availability is reconstructed and enforced, the current offline pipeline must not be described as a validated 14-day-ahead operational simulation.

This limitation must be disclosed in the PRD, evaluation results and presentation.

---

## 4. Final - Validation and delivery

**Objective:** Confirm that the MVP meets project requirements and communicate its limitations accurately.

### Tasks and current status

1. **Run the frozen model on Proof:** Corrected follow-up results are recorded in `docs/COMPARISON.md`; the prior Proof-exposure caveat is disclosed.
2. **Compare with the client baseline:** Reported savings versus Flat Rule are EUR 1,631,200.31.
3. **Confirm the walk-rate guardrail:** Frozen Proof result is 5.252 walks per 1,000 arrivals, below the maximum of 10.
4. **Review the frozen buffer:** Saved global buffer is 3 rooms; nightly implementation reads it from the saved policy.
5. **Compare business outcomes:** Frozen Proof reports 4,609 empty rooms and 131 walked guests.
6. **Document final-book limitation:** Included in the PRD and this Build Plan; presentation disclosure remains required.
7. **Complete roadmap:** `docs/ROADMAP.md` is the project evidence location; final content should be checked by the team before sign-off.
8. **Review PRD and Build Plan:** Updated to reflect implementation and evaluation evidence.
9. **Complete presentation slides:** Owned by the team presentation lead; final slide review/sign-off remains a team delivery item.
10. **Run full test suite:** 58 tests passed in the verified local run.
11. **Verify committed model/settings artifacts:** Artifact exists locally; final commit/remote availability must be confirmed before delivery.
12. **Run from a fresh checkout:** Not yet verified.

### Final completion criteria

- [x] Frozen follow-up Proof-period results are available in project evaluation evidence.
- [x] The Proof-exposure caveat is disclosed; Proof is not described as a completely untouched holdout.
- [x] Final method and parameters are documented.
- [x] Walk-rate ceiling is checked and reported for Choose and frozen Proof.
- [x] Empty rooms, walked guests, walks per 1,000 arrivals and business cost are reported.
- [x] PRD records evaluation results and implementation status.
- [ ] Final roadmap review/sign-off is not independently confirmed here.
- [x] Final-book versus 14-day booking-snapshot limitation is disclosed in the PRD and Build Plan.
- [ ] Presentation completion and accuracy review remain with the presentation lead/team.
- [ ] Saved model and settings availability from a separate fresh checkout remains to be verified.
- [x] Full local test suite passed (58 tests).
- [ ] Required challenger reviews and sign-offs with supporting commit evidence remain to be confirmed.

---

## 5. Production roadmap items

These are possible extensions beyond the MVP. Estimates are preliminary planning estimates, not completed work or committed delivery times.

| Production improvement | Purpose | Initial effort estimate |
|---|---|---:|
| Live booking-system integration | Retrieve current hotel bookings | 8 hours |
| Automated daily execution | Generate recommendations every morning | 5 hours |
| Revenue-manager dashboard | Display recommendations clearly | 10 hours |
| Model performance monitoring | Detect deterioration in prediction quality | 8 hours |
| Manual override and audit log | Allow managers to adjust recommendations and record reasons | 6 hours |
| High walk-risk alerts | Notify managers when a night approaches the walk-rate limit | 5 hours |
| As-of-date booking snapshots | Reproduce information actually available at the 14-day decision point | 10 hours |

These estimates should be refined after the production interfaces and deployment environment are defined.

---

## 6. Scope priorities

| Priority | Feature | Decision |
|---|---|---|
| Must have | Data preparation | MVP requirement |
| Must have | Cancellation prediction | MVP requirement |
| Must have | Business-cost evaluation | MVP requirement |
| Must have | Walk-rate guardrail | MVP requirement |
| Must have | Saved model and frozen settings | MVP requirement |
| Must have | Nightly recommendation table | MVP requirement |
| Should have | Uncertainty buffer comparison | Final validation |
| Should have | Clear limitation documentation | Final delivery |
| Should have | Reproducible model integration | MVP validation; fresh-checkout check open |
| Could have | Dashboard | Future production work |
| Could have | Live booking integration | Future production work |
| Could have | Automated alerts | Future production work |
| Could have | Historical booking snapshots | Future production work |
| Out of scope | Automatic booking acceptance | Not part of MVP |
| Out of scope | Automatic guest relocation | Not part of MVP |
| Out of scope | Real-time model retraining | Not part of MVP |

---

## 7. Testing and validation checklist

### Data and feature preparation

- [x] `src/contract.py` remains unchanged in the verified Build Lead work.
- [x] Feature preparation uses the Data Lead's approved interface.
- [x] Selected classifier uses the agreed 22-feature interface.
- [x] `arrival_date_year` is excluded from the selected Random Forest.
- [x] `is_canceled` is used as the target, not as a predictor.
- [x] Post-booking outcome fields are excluded from model predictors.
- [x] Prediction rows can be prepared without requiring the actual cancellation target.

### Model and evaluation

- [x] Train, Choose and Proof periods are documented.
- [x] Client baseline is included in the reported comparison.
- [x] Selected Random Forest parameters are documented.
- [x] Choose-period selection evidence is recorded.
- [x] Global buffer of 3 rooms is persisted in the selected policy.
- [x] Selected model with buffer 3 is below the Choose walk-rate ceiling (8.15 per 1,000).
- [x] Frozen follow-up Proof metrics are reported.
- [ ] Proof has not been represented as a completely untouched holdout; the earlier exploratory exposure is explicitly disclosed.
- [x] No model or buffer retuning is claimed after the corrected frozen follow-up; the earlier exposure caveat remains disclosed.

### Nightly pipeline

- [x] Selected model and preprocessing pipeline load successfully in the current environment.
- [x] Nightly script loads frozen settings.
- [x] Positive probability class represents `is_canceled = 1`.
- [x] One finite probability between 0 and 1 is generated per booking and validated.
- [x] Input row association is preserved before aggregation.
- [x] Predictions are aggregated by hotel and arrival date.
- [x] Global buffer calculation matches the saved policy implementation.
- [x] Verified output covers the requested 14-night period.
- [x] Output contains all six required columns.
- [x] Local output values are valid.
- [x] Nightly pipeline does not retrain or retune the model.
- [ ] Fresh-checkout execution is not yet tested.
- [ ] Genuine historical T-14 booking availability is not yet validated.

### Final documentation and delivery

- [x] Final-book versus 14-day booking-snapshot limitation is documented.
- [x] `pytest -q` completed with 58 passing tests in the verified run.
- [x] PRD reflects actual implementation and reported evaluation results.
- [ ] Final roadmap review/sign-off is not independently confirmed.
- [x] Numerical model and business results are copied from project evaluation evidence, not estimated.
- [ ] Challenger review and sign-off remain to be confirmed.
- [ ] Presentation slides must be checked by the presentation lead/team for implementation accuracy and limitation disclosure.
- [ ] Fresh-checkout artifact availability and reproducibility remain to be verified.

---

## 8. Build Lead responsibilities

The Build Lead is responsible for:

1. Maintaining the project architecture and build plan.
2. Coordinating interfaces between feature preparation, model training and nightly prediction.
3. Coordinating with the Model Lead to confirm saved-model and settings interfaces.
4. Developing and validating `src/nightly.py`.
5. Ensuring the nightly pipeline uses the saved model without retraining or retuning.
6. Validating probability outputs, row association, aggregation and recommendation-table structure.
7. Maintaining `AGENTS.md`.
8. Maintaining `docs/PRD.md` and `docs/ROADMAP.md`.
9. Tracking team dependencies and unresolved decisions.
10. Ensuring implementation follows the evaluation contract.
11. Reviewing final deliverables before submission.
12. Coordinating Build Lead input to the presentation; slide production remains with the designated presentation lead/team.

**Completion principle:** A document is not considered complete merely because it exists. It must reflect the actual implementation or decision, be tested where applicable, and be supported by evidence. Open items must remain visibly open rather than being marked complete without verification.
