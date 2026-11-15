# What did the AI build get wrong, and what did it expose in ours?

**Owner:** Data Lead. **Challenger:** Build Lead. **When:** started on Thursday, finished on Friday.

Compare your build on `main` with the AI build on the `ai-benchmark` branch, row by row. Every cell points to a file and a line, or to a log excerpt. "Same" is an acceptable verdict when it is true.

| Row | Our build | AI build | Verdict |
|---|---|---|---|
| What counts as a cancellation, and which bookings are scored | `is_canceled` is the target; approved booking-time features are documented in `docs/COLUMNS.md`. | Reconstructed benchmark scores every local booking and uses `is_canceled`; see `ai_benchmark/PLAN_AI.md` and `ai_benchmark/run.py`. | Comparable; newly reconstructed, not historical |
| Unit of decision (night or booking) | Booking probabilities are aggregated by hotel and arrival date in `src/nightly.py`. | `contract.nightly_table` aggregates probabilities by hotel and arrival date; see `ai_benchmark/run.py`. | Same unit |
| Columns used, and the bin each sits in | The approved 22-feature classifier interface is documented in `src/models/classifiers.py` and `docs/COLUMNS.md`. | 23 fixed-at-booking columns; target/status/amendable fields excluded; see `ai_benchmark/PLAN_AI.md`. | Same leakage control |
| Split (time or random), and where the buffer was chosen | `src/backtest.py` uses Train/Choose/Proof chronologically and freezes the buffer on Choose. | Chronological Train/Choose/Proof; integer buffer selected on Choose and frozen; see `ai_benchmark/RESULT.md`. | Same split discipline |
| Baselines run before any model | The required client flat-rule reference is evaluated alongside the selected policy. | Required Train-rate flat rule, with Choose-selected buffer, is reported in `ai_benchmark/RESULT.md`. | Same required baseline |
| Walk ceiling respected on the choose period and reported on proof | Choose: 8.15 walks per 1,000; frozen Proof: 5.252; both are below 10. | Model Choose: 1.55; model Proof: 2.85; both below 10; see `ai_benchmark/RESULT.md`. | Ceiling met |
| Euros, rooms and walks per 1,000 on the proof period | EUR 2,251,729.23; 4,609 empty rooms; 131 walked guests; 5.252 walks per 1,000. | EUR 2,890,485.30; 5,884 empty rooms; 71 walked guests; 2.85 walks per 1,000; see `ai_benchmark/RESULT.md`. | Comparable evidence; not historical |
| Runs end to end with one command | `python src/backtest.py` and `python src/nightly.py --from 2017-08-18 --nights 14` pass from committed `HEAD`. | `python ai_benchmark\run.py` completed and wrote the 14-night CSV; see `ai_benchmark/RESULT.md`. | Verified |
| Lines of code a team member can explain | The persisted policy, feature interface and nightly loader are documented in `docs/BUILD_PLAN.md`. | Small standalone script, plan, captured output, and limitation note in `ai_benchmark/`. | Reconstructed evidence available |

## Corrected Train-Choose-Freeze-Proof evidence (2026-11-16)

The corrected follow-up fit candidate models on Train, selected the policy on Choose by the highest AUC among candidates satisfying the walk ceiling, froze the Random Forest policy with buffer 3, and persisted it to `models/selected_policy.joblib` before Proof scoring. Proof was then evaluated only for the frozen Random Forest and the required client flat-rule reference. These are the reported results for the corrected follow-up; `output.txt` remains the separate historical record of the earlier all-candidates Proof run.

| Choose selection evidence | Result |
|---|---:|
| Selected model and frozen buffer | Random Forest, 3 |
| Choose AUC | 0.821727 |
| Choose MAE | 7.432268 |
| Choose walks per 1,000 | 8.15 (ceiling: 10) |
| Choose cost | EUR 1,384,174.34 |
| Savings versus flat rule | EUR 1,003,755.30 |

| Frozen Proof policy | Result |
|---|---:|
| Model and buffer | Random Forest, 3 |
| AUC | 0.827749 |
| MAE | 7.710066 |
| Empty rooms | 4,609 |
| Walked guests | 131 |
| Walks per 1,000 | 5.252 (ceiling satisfied; maximum 10) |
| Cost | EUR 2,251,729.23 |
| Savings versus flat rule | EUR 1,631,200.31 |

The prior Proof exposure means this corrected follow-up demonstrates the corrected execution order, but it must not be described as evaluation on a completely untouched holdout. The data is a static final-book export; these results do not reconstruct a genuine historical T-14 booking snapshot.

## Which gaps in our build did the AI build expose?

_Up to three, each naming a file and line in our build, or an excerpt from a log. If you found none, say so and name the file that shows it._

<!-- answer:4 -->

The reconstructed benchmark does not establish a genuine historical T-14 workflow because it also uses the final-book export; this limitation is recorded in `ai_benchmark/RESULT.md`. Its proof cost is higher than the corrected production follow-up, so it is evidence for comparison rather than a replacement.

## Which mistakes did the AI build make that ours did not?

_Up to three, each naming a file and line on the `ai-benchmark` branch. If you found none, say so and name the file that shows it._

<!-- answer:4 -->

No historical AI-build mistakes can be established: this is explicitly a newly reconstructed benchmark, not the missing historical branch. The reconstructed implementation is independently documented in `ai_benchmark/PLAN_AI.md` and `ai_benchmark/run.py`.

## What would we take from the AI build, and what would we never ship?

_Two sentences, each pointing to a file and line._

<!-- answer:2 -->

The project can retain the benchmark's explicit booking-time feature audit and captured one-command evidence in `ai_benchmark/PLAN_AI.md` and `ai_benchmark/RESULT.md`. It must never ship target leakage, post-booking outcome fields, or buffer tuning on Proof; those controls are enforced and documented in `src/features.py`, `src/backtest.py` and `docs/DECISIONS.md`.
