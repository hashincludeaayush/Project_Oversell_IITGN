"""Create nightly recommendations from the saved policy and static booking export.

The historical export is a final-book snapshot. This command does not recreate the
bookings known at a past decision time and is not a validated T-14 simulation.
"""

import argparse
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

import contract
import data
import features
from models.helpers import predict_cancellation_probability
from models.persistence import load_selected_policy

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = ROOT / "models" / "selected_policy.joblib"
DEFAULT_OUTPUT_PATH = ROOT / "output" / "nightly_recommendations.csv"

OUTPUT_COLUMNS = [
    "hotel",
    "arrival_date",
    "bookings_on_book",
    "actual_cancellations",
    "expected_cancellations",
    "cancellation_spread",
    "stay_value",
    "buffer",
    "recommended_oversell",
]


def parse_start_date(value):
    """Parse a strict YYYY-MM-DD date for the inclusive window start."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("Start date must use YYYY-MM-DD format.")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Start date must be a valid date in YYYY-MM-DD format.") from exc
    if parsed.isoformat() != value:
        raise ValueError("Start date must use YYYY-MM-DD format.")
    return parsed


def _validate_nights(nights):
    if isinstance(nights, (bool, np.bool_)) or not isinstance(nights, (int, np.integer)):
        raise ValueError("Number of nights must be a positive whole number.")
    if int(nights) <= 0:
        raise ValueError("Number of nights must be greater than zero.")
    return int(nights)


def _load_policy(model_path):
    try:
        return load_selected_policy(model_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Selected model artifact was not found: {model_path}") from exc
    except Exception as exc:
        raise ValueError(f"Could not load selected model artifact at {model_path}: {exc}") from exc


def _recommendation_table(nights_table, buffer):
    table = nights_table.reset_index().rename(
        columns={
            "book": "bookings_on_book",
            "cancelled": "actual_cancellations",
            "expected": "expected_cancellations",
            "spread": "cancellation_spread",
        }
    )
    table["buffer"] = int(buffer)
    oversell = np.maximum(
        0,
        np.round(table["expected_cancellations"].to_numpy(dtype=float) - int(buffer)),
    )
    table["recommended_oversell"] = oversell.astype(np.int64)
    table["arrival_date"] = pd.to_datetime(table["arrival_date"]).dt.strftime("%Y-%m-%d")
    return table.loc[:, OUTPUT_COLUMNS]


def _validate_calendar_coverage(nights_table, hotels, expected_dates):
    observed_dates = nights_table.index.get_level_values("arrival_date").unique()
    missing_dates = pd.Index(expected_dates).difference(observed_dates)
    expected_pairs = pd.MultiIndex.from_product(
        [hotels, expected_dates],
        names=nights_table.index.names,
    )
    missing_pairs = expected_pairs.difference(nights_table.index)

    if missing_dates.empty and missing_pairs.empty:
        return

    details = []
    if not missing_dates.empty:
        details.append(
            "missing arrival dates: "
            + ", ".join(pd.Timestamp(value).date().isoformat() for value in missing_dates)
        )
    if not missing_pairs.empty:
        formatted_pairs = [
            f"({hotel}, {pd.Timestamp(arrival).date().isoformat()})"
            for hotel, arrival in missing_pairs
        ]
        details.append("missing hotel/date combinations: " + ", ".join(formatted_pairs))
    raise ValueError(
        "Requested window contains zero-booking nights; the evaluation contract "
        "does not define stay value for them (" + "; ".join(details) + ")."
    )


def run_nightly(
    start_date,
    nights,
    *,
    model_path=DEFAULT_MODEL_PATH,
    output_path=DEFAULT_OUTPUT_PATH,
):
    """Load the frozen policy, score a date window, and export its nightly table."""
    start = parse_start_date(start_date)
    number_of_nights = _validate_nights(nights)
    end = start + timedelta(days=number_of_nights)

    policy = _load_policy(model_path)
    raw = data.read_raw()
    if "is_canceled" not in raw.columns:
        raise ValueError(
            "The static booking export must include is_canceled for retrospective contract aggregation."
        )

    # Keep the target out of the predictor frame. Add it back only for the
    # contract's retrospective cancellation summary after predictions exist.
    prepared = features.prepare_bookings(raw, require_target=False)
    date_mask = prepared["arrival_date"].ge(pd.Timestamp(start)) & prepared[
        "arrival_date"
    ].lt(pd.Timestamp(end))
    filtered = prepared.loc[date_mask].copy()
    if filtered.empty:
        raise ValueError(
            f"No bookings arrive from {start.isoformat()} through "
            f"{(end - timedelta(days=1)).isoformat()}."
        )

    model_inputs = features.model_features(filtered)
    probabilities = np.asarray(
        predict_cancellation_probability(policy["model"], model_inputs),
        dtype=float,
    )
    if probabilities.ndim != 1 or len(probabilities) != len(filtered):
        raise ValueError("The saved model must return one probability per filtered booking row.")
    if not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError("The saved model returned probabilities outside the finite [0, 1] range.")

    scoring_rows = filtered.copy()
    scoring_rows["is_canceled"] = raw.loc[filtered.index, "is_canceled"].to_numpy()
    nightly = contract.nightly_table(scoring_rows, probabilities)
    expected_dates = pd.date_range(start=start, periods=number_of_nights, freq="D")
    hotels = sorted(raw["hotel"].dropna().unique().tolist())
    _validate_calendar_coverage(nightly, hotels, expected_dates)
    recommendations = _recommendation_table(nightly, policy["buffer"])

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    recommendations.to_csv(destination, index=False)
    return recommendations


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Write nightly recommendations from the saved policy. The static historical "
            "export is a final-book snapshot, not a reconstructed historical T-14 snapshot."
        )
    )
    parser.add_argument(
        "--from",
        dest="start_date",
        type=parse_start_date,
        required=True,
        help="inclusive first arrival date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--nights",
        type=int,
        required=True,
        help="number of calendar arrival dates to include",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"CSV output path (default: {DEFAULT_OUTPUT_PATH})",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        recommendations = run_nightly(
            args.start_date,
            args.nights,
            output_path=args.output,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Wrote {len(recommendations)} nightly rows to {args.output}")
    return 0


if __name__ == "__main__":
    main()
