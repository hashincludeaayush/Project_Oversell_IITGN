# What lives in src, and who writes it?

| File | Status | Owner | Its one job |
|---|---|---|---|
| `data.py` | Given | | Download the bookings and read them exactly as exported |
| `contract.py` | Given, never edited | | The client's scoring rule |
| `features.py` | Yours | Data Lead | Clean the bookings and return the columns your methods may use, with every choice logged in `docs/DECISIONS.md` |
| `backtest.py` | Yours | Model Lead | Fit methods on Train, select the method and buffer on Choose, freeze and save the selected policy to `models/` before Proof, then evaluate the frozen policy and required flat-rule reference |
| `nightly.py` | Yours | Build Lead | Read a bookings file and the saved method, and write the oversell table for the nights asked for |

Commit `models/selected_policy.joblib` after the Train/Choose selection and freeze step. The nightly command loads this saved policy without retraining. The corrected Proof evaluation has not yet been rerun; see `docs/DECISIONS.md` for the historical protocol note. The nightly CSV defaults to `output/nightly_recommendations.csv`; pass `--output` to choose another path. The dataset is a static final-book export, so this command does not reconstruct a genuine historical T-14 snapshot.

```bash
python src/backtest.py
python src/nightly.py --from 2017-08-18 --nights 14
```
