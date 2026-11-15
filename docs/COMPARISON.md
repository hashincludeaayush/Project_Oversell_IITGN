# What did the AI build get wrong, and what did it expose in ours?

**Owner:** Data Lead. **Challenger:** Build Lead. **When:** started on Thursday, finished on Friday.

Compare your build on `main` with the AI build on the `ai-benchmark` branch, row by row. Every cell points to a file and a line, or to a log excerpt. "Same" is an acceptable verdict when it is true.

| Row | Our build | AI build | Verdict |
|---|---|---|---|
| What counts as a cancellation, and which bookings are scored | | | |
| Unit of decision (night or booking) | | | |
| Columns used, and the bin each sits in | | | |
| Split (time or random), and where the buffer was chosen | | | |
| Baselines run before any model | | | |
| Walk ceiling respected on the choose period and reported on proof | | | |
| Euros, rooms and walks per 1,000 on the proof period | | | |
| Runs end to end with one command | | | |
| Lines of code a team member can explain | | | |

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

## Which mistakes did the AI build make that ours did not?

_Up to three, each naming a file and line on the `ai-benchmark` branch. If you found none, say so and name the file that shows it._

<!-- answer:4 -->

## What would we take from the AI build, and what would we never ship?

_Two sentences, each pointing to a file and line._

<!-- answer:2 -->
