# Build Plan
## Project Oversell â€“ Hotel Overbooking Recommendation System

**Owner:** Build Lead
**Project:** IIT Gandhinagar â€“ Week 6 Build
**Objective:** Build, test and deliver a working hotel overbooking recommendation pipeline.

---

## 1. Build phases

| Phase | Deliverable | Owner | Planned hours | Actual hours | Done when | Evidence |
|---|---|---|---:|---:|---|---|

| POC | Data preparation and feature pipeline | Data Lead | 4 | 3 | Approved booking-time features are prepared correctly | `src/features.py`, `docs/COLUMNS.md` |
| POC | Leakage and AUC experiment | Data Lead | 3 | 4 | Valid, leaked and random-split AUCs are compared and documented | `src/phase8_leakage_auc.py`, `notebooks/05_leakage_auc_experiment.ipynb`, `docs/PHASE8_FINDINGS.md` |
| POC | Exploratory data analysis and modeling hypotheses | Data Lead | 6 | 7 | Cancellation patterns are explored and testable, leakage-safe modeling hypotheses are documented | `notebooks/04_exploratory_insights.ipynb`, `docs/PHASE8_FINDINGS.md` |
| POC | Candidate model and baseline comparison | Model Lead | 6 | To be updated | Candidate methods are evaluated using the agreed business and model-selection metrics | `src/backtest.py`, `docs/COMPARISON.md` |
| POC | Business-cost and walk-rate validation | Model Lead | 3 | To be updated | Empty rooms, walked guests, cost and walk rate are calculated using the contract | Backtest output |
| MVP | Nightly recommendation pipeline | Build Lead | 6 | To be updated | The script generates recommendations for the requested hotel-arrival nights | `src/nightly.py` |
| MVP | Model integration | Build Lead and Model Lead | 3 | To be updated | Nightly pipeline successfully loads the selected model and frozen settings | Integration test |
| MVP | Output validation | Build Lead | 1 | To be updated | Output contains all required columns and valid recommendations | Generated output file |
| Final | Proof-period evaluation review | Model Lead | 2 | To be updated | Frozen method is evaluated on Proof without further tuning | Backtest results |
| Final | Uncertainty buffer review | Model Lead and Build Lead | 2 | To be updated | Frozen buffer approach is verified and documented | Comparison results |
| Final | Full-night caveat and roadmap | Build Lead and Client Lead | 2 | To be updated | Final-book limitation and future improvements are documented | `docs/ROADMAP.md`, PRD |
| Final | Documentation and presentation | All team members | 3 | To be updated | Required documents and slides are complete and reviewed | Project documents and slides |

**Note:** Planned hours are initial estimates for team discussion, not committed actual effort. Actual hours must be updated from the team's time spent.

---

## 2. POC â€“ Proof of Concept

**Objective:** Establish whether the available booking data can support a reliable overbooking recommendation.

### Tasks

1. Inspect the dataset and understand its structure.
2. Identify the booking-time columns that are safe to use.
3. Prepare the model features using the Data Lead's approved feature pipeline.
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
- The Train, Choose and Proof periods are kept separate.
- The walk-rate ceiling is checked.
- Results are documented with actual outputs.
- Model-selection decisions and their supporting evidence are recorded.

### Evidence files

- `src/features.py`
- `src/backtest.py`
- `docs/COLUMNS.md`
- `docs/COMPARISON.md`
- `docs/DECISIONS.md`
- `docs/EVALUATION_CONTRACT.md`

---

## 3. MVP â€“ Minimum Viable Product

**Objective:** Generate a usable 14-night overbooking recommendation table for the two hotels.

### 3.1 Selected model and settings

The Model Lead has confirmed the following selected machine-learning model:

| Setting | Confirmed value |
|---|---|
| Model | Random Forest |
| Number of estimators | 100 |
| Maximum depth | 12 |
| Minimum samples per leaf | 20 |
| Choose-period AUC | 0.8217 |
| Logistic Regression Choose-period AUC | 0.8168 |
| Frozen global buffer | 3 rooms |

The selected Random Forest uses the 22-feature `FEATURE_COLUMNS` interface defined by the Model Lead in `src/models/classifiers.py`.

The Data Lead's `features.MODEL_FEATURES` interface contains 23 approved booking-time predictors. The selected Random Forest intentionally excludes `arrival_date_year` because the training period contains 2015 and 2016, whereas the Proof period and intended later use contain 2017 onward. Seasonality is represented through arrival month and week number.

The saved model's feature list, order, types and preprocessing must remain consistent during nightly inference.

The model-selection AUC is not a substitute for business-cost and walk-rate validation. The selected policy must still be checked against the Choose-period walk-rate ceiling and evaluated on the frozen Proof period.

### 3.2 Model integration agreement

Before implementing `src/nightly.py`, the Model Lead and Build Lead must confirm:

1. **Selected model:** Random Forest with 100 estimators, maximum depth 12 and minimum samples per leaf 20.
2. **Selected features:** The 22-feature `FEATURE_COLUMNS` interface, with `arrival_date_year` intentionally excluded.
3. **Saved artifact:** Exact model filename, directory and serialization format under `models/`.
4. **Preprocessing:** The saved artifact must include the fitted preprocessing pipeline used during training.
5. **Loading interface:** Exact method for loading the saved model from `src/nightly.py`.
6. **Prediction interface:** Exact prediction method and confirmation that probability class 1 represents `is_canceled = 1`.
7. **Frozen settings:** One global buffer of 3 rooms, saved in the agreed settings format.
8. **Buffer calculation:** Integer rounding and non-negative handling must match the Model Lead's committed implementation in `src/models/buffer.py`.
9. **Choose-period validation:** Confirm that the selected Random Forest with buffer 3 satisfies the walk-rate ceiling on Choose.
10. **Reproducibility:** A fresh checkout must be able to run the nightly script without retraining or retuning the model.

The Build Lead must not invent an artifact filename or independently recreate the Model Lead's preprocessing, feature interface or buffer logic.

### 3.3 Nightly recommendation pipeline

**File:** `src/nightly.py`
**Owner:** Build Lead

### Tasks

1. Create `src/nightly.py`.
2. Read the booking input data.
3. Prepare booking rows using the Data Lead's approved `features.prepare_bookings()` interface, supporting prediction rows that do not contain the actual cancellation target.
4. Use the selected model's exact 22-feature `FEATURE_COLUMNS` interface.
5. Load the committed Random Forest pipeline and frozen settings from `models/`.
6. Generate one cancellation probability per booking.
7. Confirm that every probability is finite and between 0 and 1.
8. Preserve booking-row order when associating predictions with the original bookings.
9. Aggregate booking counts and predicted cancellation probabilities by `hotel` and `arrival_date`.
10. Calculate expected cancellations from the sum of booking-level cancellation probabilities.
11. Apply the frozen global buffer of 3 rooms using the Model Lead's verified calculation.
12. Calculate the recommended oversell quantity.
13. Generate the required recommendation table.
14. Validate the output and run tests.

The nightly script must not:

- Retrain the model.
- Refit preprocessing.
- Retune the buffer.
- Select a different model.
- Use actual cancellation outcomes to generate predictions.
- Use post-booking outcome fields as model predictors.

### Required output columns

| Column | Meaning |
|---|---|
| `hotel` | Hotel name |
| `arrival_date` | Arrival night |
| `bookings_on_book` | Number of booking records included in the prediction input for that hotel and arrival night |
| `expected_cancellations` | Sum of cancellation probabilities for those bookings |
| `buffer` | Frozen global safety margin of 3 rooms |
| `recommended_oversell` | Recommended oversell quantity |

### Oversell calculation

The conceptual relationship is:

`Recommended oversell = Expected cancellations - Safety buffer`

The actual integer conversion, rounding and non-negative handling must match the Model Lead's committed implementation in `src/models/buffer.py`.

The Build Lead must not independently change the calculation or introduce hotel-specific buffers without a formally agreed change to the methodology.

### MVP completion criteria

- The nightly script executes successfully.
- The selected Random Forest model is loaded correctly.
- The saved preprocessing pipeline is included and used.
- The model uses the agreed 22-feature interface.
- `arrival_date_year` is excluded from the selected classifier.
- The frozen global buffer of 3 rooms is loaded correctly.
- The script generates one finite cancellation probability between 0 and 1 per input booking.
- Prediction order is preserved before aggregation.
- The script generates one row per required hotel and arrival night.
- The output covers the requested 14-night period.
- The output contains all six required columns.
- All output values are valid.
- The script does not retrain or retune the model or buffer.
- The script does not modify `src/contract.py`.
- The output can be reproduced from the same inputs and saved model.
- A fresh checkout can execute the nightly pipeline without first running model training.

### Expected command

```powershell
python src/nightly.py --from 2017-08-18 --nights 14
```

The exact output filename, model-loading interface and settings format must match the implementation agreed with the Model Lead.

### Important operational limitation

The available dataset represents final booking information and does not automatically provide historical booking snapshots.

A genuine 14-day-ahead recommendation requires only bookings that existed on or before the simulated decision date. Unless historical booking-time availability is reconstructed and enforced, the current offline pipeline must not be described as a validated 14-day-ahead operational simulation.

This limitation must be disclosed in the PRD, evaluation results and presentation.

---

## 4. Final â€“ Validation and delivery

**Objective:** Confirm that the MVP meets the project requirements and clearly communicate its limitations.

### Tasks

1. Run the frozen model on the Proof period.
2. Compare the selected approach against the client baseline.
3. Confirm the walk-rate guardrail.
4. Review and verify the frozen global buffer.
5. Compare business cost, empty rooms and walked guests.
6. Document the final-book versus 14-day-on-book limitation.
7. Complete the product roadmap.
8. Review the PRD and Build Plan.
9. Complete and validate presentation slides.
10. Run the complete test suite.
11. Verify that all required model and settings artifacts are committed.
12. Confirm that the nightly pipeline works from a fresh checkout.

### Final completion criteria

- Proof-period results are available from the actual backtest.
- No tuning has been performed using Proof results.
- The final method and its parameters are documented.
- The selected method's walk-rate ceiling is checked and reported.
- Total empty rooms, walked guests, walks per 1,000 arrivals and total business cost in EUR are reported.
- The PRD contains actual evaluation results.
- The roadmap identifies production improvements.
- The final-book versus 14-day booking-snapshot limitation is clearly disclosed.
- The required documents and presentation are ready.
- The saved model and settings are reproducible from a fresh checkout.
- The complete test suite passes.
- Required challenger reviews and sign-offs are completed with supporting commit evidence.

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

These estimates are preliminary planning estimates, not completed work or committed delivery times.

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
| Should have | Reproducible model integration | MVP validation |
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

- [ ] `src/contract.py` remains unchanged.
- [ ] Feature preparation uses the Data Lead's approved interface.
- [ ] The selected classifier uses the agreed 22-feature interface.
- [ ] `arrival_date_year` is excluded from the selected Random Forest.
- [ ] `is_canceled` is used only as the prediction target.
- [ ] No post-booking information is used as a model predictor.
- [ ] Prediction rows can be prepared without requiring the actual cancellation target.

### Model and evaluation

- [ ] Train, Choose and Proof periods are separated.
- [ ] The client baseline is included.
- [ ] The selected Random Forest parameters are documented.
- [ ] The Choose-period selection evidence is recorded.
- [ ] The global buffer of 3 rooms is saved.
- [ ] The selected model with buffer 3 is checked against the Choose-period walk-rate ceiling.
- [ ] The frozen Proof evaluation reports business-cost metrics.
- [ ] No tuning is performed using Proof results.

### Nightly pipeline

- [ ] The selected model and preprocessing pipeline load successfully.
- [ ] The nightly script loads the frozen settings.
- [ ] The positive probability class represents `is_canceled = 1`.
- [ ] One finite probability between 0 and 1 is generated per booking.
- [ ] Prediction order is preserved.
- [ ] Predictions are aggregated by hotel and arrival date.
- [ ] The global buffer calculation matches the Model Lead's implementation.
- [ ] The output covers the requested 14-night period.
- [ ] The output contains all six required columns.
- [ ] All output values are valid.
- [ ] The nightly pipeline does not retrain or retune the model.
- [ ] The fresh-checkout execution is tested.

### Final documentation and delivery

- [ ] The final-book versus 14-day booking-snapshot limitation is documented.
- [ ] `pytest -q` passes.
- [ ] The PRD and roadmap reflect actual project results.
- [ ] No numerical results are estimated or fabricated.
- [ ] The challenger has reviewed and signed the relevant artifact.
- [ ] Required sign-offs include supporting commit evidence.
- [ ] Presentation slides accurately describe the implemented MVP and its limitations.

---

## 8. Build Lead responsibilities

The Build Lead is responsible for:

1. Maintaining the project architecture and build plan.
2. Coordinating interfaces between feature preparation, model training and nightly prediction.
3. Coordinating with the Model Lead to confirm saved-model and settings interfaces.
4. Developing and validating `src/nightly.py`.
5. Ensuring the nightly pipeline uses the saved model without retraining or retuning.
6. Validating probability outputs, row ordering, aggregation and recommendation-table structure.
7. Maintaining `AGENTS.md`.
8. Maintaining `docs/PRD.md` and `docs/ROADMAP.md`.
9. Tracking team dependencies and unresolved decisions.
10. Ensuring the implementation follows the evaluation contract.
11. Reviewing the final deliverables before submission.
12. Preparing and validating the Build Lead presentation slides.

**Important:** A document is not considered complete merely because it exists. It must be implemented or reviewed, tested where applicable, and supported by evidence.
