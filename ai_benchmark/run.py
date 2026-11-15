"""Independent, reconstructed AI benchmark for the oversell project."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import contract  # noqa: E402


FEATURES = [
    "hotel", "lead_time", "arrival_date_year", "arrival_date_month",
    "arrival_date_week_number", "arrival_date_day_of_month",
    "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children",
    "babies", "meal", "country", "market_segment", "distribution_channel",
    "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled", "reserved_room_type", "deposit_type",
    "agent", "company", "customer_type",
]
NUMERIC = [
    "lead_time", "arrival_date_year", "arrival_date_week_number",
    "arrival_date_day_of_month", "stays_in_weekend_nights",
    "stays_in_week_nights", "adults", "children", "babies",
    "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled",
]
CATEGORICAL = [column for column in FEATURES if column not in NUMERIC]


def load_bookings() -> pd.DataFrame:
    """Load and prepare only the raw fields needed by this benchmark."""
    frame = pd.read_csv(ROOT / "data" / "hotels.csv")
    frame["arrival_date"] = pd.to_datetime(
        frame["arrival_date_year"].astype(str) + "-"
        + frame["arrival_date_month"] + "-"
        + frame["arrival_date_day_of_month"].astype(str),
        format="%Y-%B-%d",
    )
    frame["nights"] = (
        frame["stays_in_weekend_nights"] + frame["stays_in_week_nights"]
    )
    frame["children"] = frame["children"].fillna(0)
    for column in ("country", "meal"):
        frame[column] = frame[column].fillna("Unknown").astype(str)
    for column in ("agent", "company"):
        frame[column] = frame[column].fillna("None").map(
            lambda value: str(int(value)) if isinstance(value, float) and value.is_integer()
            else str(value)
        )
    return frame


def make_model() -> Pipeline:
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("one_hot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return Pipeline([
        ("features", ColumnTransformer([
            ("numeric", numeric, NUMERIC),
            ("categorical", categorical, CATEGORICAL),
        ])),
        ("classifier", LogisticRegression(max_iter=400, random_state=42)),
    ])


def policy_metrics(bookings: pd.DataFrame, probabilities: np.ndarray, buffer: int):
    nights = contract.nightly_table(
        bookings[["hotel", "arrival_date", "is_canceled", "adr", "nights"]],
        probabilities,
    )
    oversell = np.maximum(np.rint(nights["expected"] - buffer), 0)
    return nights, contract.night_cost(nights, oversell)


def select_buffer(bookings: pd.DataFrame, probabilities: np.ndarray):
    candidates = []
    for buffer in range(31):
        nights, metrics = policy_metrics(bookings, probabilities, buffer)
        if metrics["ceiling_met"]:
            candidates.append((metrics["cost_eur"], buffer, nights, metrics))
    if not candidates:
        raise RuntimeError("No buffer from 0 through 30 meets the walk ceiling.")
    _, buffer, nights, metrics = min(candidates, key=lambda item: (item[0], item[1]))
    return buffer, nights, metrics


def fmt(metrics: dict) -> str:
    return (
        f"cost_eur={metrics['cost_eur']:.2f}, empty_rooms={metrics['empty_rooms']}, "
        f"walked_guests={metrics['walked_guests']}, "
        f"walks_per_1000={metrics['walks_per_1000']:.2f}, "
        f"ceiling_met={metrics['ceiling_met']}, nights={metrics['nights']}"
    )


def main() -> None:
    frame = load_bookings()
    train, choose, proof = contract.split_periods(frame)

    model = make_model()
    model.fit(train[FEATURES], train["is_canceled"])
    choose_prob = np.asarray(model.predict_proba(choose[FEATURES])[:, 1], dtype=float)
    proof_prob = np.asarray(model.predict_proba(proof[FEATURES])[:, 1], dtype=float)
    if not np.isfinite(proof_prob).all() or ((proof_prob < 0) | (proof_prob > 1)).any():
        raise RuntimeError("Model produced an invalid cancellation probability.")

    model_buffer, choose_nights, choose_metrics = select_buffer(choose, choose_prob)
    _, proof_metrics = policy_metrics(proof, proof_prob, model_buffer)

    train_rates = train.groupby("hotel")["is_canceled"].mean()
    choose_flat_prob = choose["hotel"].map(train_rates).fillna(train["is_canceled"].mean()).to_numpy()
    proof_flat_prob = proof["hotel"].map(train_rates).fillna(train["is_canceled"].mean()).to_numpy()
    flat_buffer, _, flat_choose_metrics = select_buffer(choose, choose_flat_prob)
    _, flat_proof_metrics = policy_metrics(proof, proof_flat_prob, flat_buffer)

    requested_mask = (
        (proof["arrival_date"] >= "2017-08-18")
        & (proof["arrival_date"] <= "2017-08-31")
    )
    requested = proof[
        requested_mask
    ].copy()
    requested_prob = proof_prob[requested_mask.to_numpy()]
    requested_nights = contract.nightly_table(
        requested[["hotel", "arrival_date", "is_canceled", "adr", "nights"]],
        requested_prob,
    ).reset_index()
    requested_nights["buffer"] = model_buffer
    requested_nights["oversell"] = np.maximum(
        np.rint(requested_nights["expected"] - model_buffer), 0
    ).astype(int)
    requested_nights = requested_nights[
        ["hotel", "arrival_date", "book", "expected", "buffer", "oversell"]
    ].sort_values(["arrival_date", "hotel"])
    output_path = Path(__file__).resolve().parent / "oversell_2017-08-18_31.csv"
    requested_nights.to_csv(output_path, index=False)

    print("RECONSTRUCTED AI BENCHMARK (new; not historical AI results)")
    print(
        f"rows={len(frame)}, train={len(train)}, choose={len(choose)}, "
        f"proof={len(proof)}, proof_dates={proof['arrival_date'].min().date()}.."
        f"{proof['arrival_date'].max().date()}"
    )
    print(f"features={len(FEATURES)} fixed-at-booking; model=logistic_regression")
    print(
        f"CHOOSE model: buffer={model_buffer}, "
        f"auc={roc_auc_score(choose['is_canceled'], choose_prob):.6f}, "
        f"{fmt(choose_metrics)}"
    )
    print(
        f"CHOOSE flat: buffer={flat_buffer}, "
        f"auc={roc_auc_score(choose['is_canceled'], choose_flat_prob):.6f}, "
        f"{fmt(flat_choose_metrics)}"
    )
    print(
        f"PROOF model: auc={roc_auc_score(proof['is_canceled'], proof_prob):.6f}, "
        f"{fmt(proof_metrics)}"
    )
    print(
        f"PROOF flat: {fmt(flat_proof_metrics)}, "
        f"savings_eur={flat_proof_metrics['cost_eur'] - proof_metrics['cost_eur']:.2f}"
    )
    print(f"14-night table: {output_path}")
    print(requested_nights.to_string(index=False))


if __name__ == "__main__":
    main()
