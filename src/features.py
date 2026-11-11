"""Prepare booking-time features without changing the raw booking export."""

from __future__ import annotations

import pandas as pd

from data import arrival_date

MODEL_FEATURES: tuple[str, ...] = (
    "hotel",
    "lead_time",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "meal",
    "country",
    "market_segment",
    "distribution_channel",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "reserved_room_type",
    "deposit_type",
    "agent",
    "company",
    "customer_type",
)

SCORING_COLUMNS: tuple[str, ...] = (
    "hotel",
    "arrival_date",
    "is_canceled",
    "adr",
    "nights",
)

FORBIDDEN_MODEL_COLUMNS: frozenset[str] = frozenset(
    {"is_canceled", "reservation_status", "reservation_status_date"}
)

_REQUIRED_RAW_COLUMNS: tuple[str, ...] = tuple(
    column
    for column in MODEL_FEATURES
    if column not in {"hotel"}
) + (
    "hotel",
    "arrival_date_year",
    "arrival_date_month",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adr",
)


def _validate_model_features() -> None:
    """Keep the feature contract visibly separate from outcome columns."""
    forbidden = set(MODEL_FEATURES).intersection(FORBIDDEN_MODEL_COLUMNS)
    if forbidden:
        raise ValueError(f"Outcome columns cannot be model features: {sorted(forbidden)}")


def _category_values(series: pd.Series, missing_label: str) -> pd.Series:
    """Convert identifiers to stable categories without a float suffix."""
    values = series.fillna(missing_label)

    def format_value(value: object) -> str:
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    return values.map(format_value).astype("string")


def prepare_bookings(
    raw: pd.DataFrame,
    *,
    require_target: bool = True,
) -> pd.DataFrame:
    """Return a clean, model-ready view of raw bookings.

    The input is never mutated. Missing categorical values are represented by
    explicit categories, while the raw export remains available to scoring and
    audit code. The returned frame contains booking-time model features plus
    the derived/scoring columns needed by the contract.
    """
    _validate_model_features()
    required = set(_REQUIRED_RAW_COLUMNS)
    if require_target:
        required.add("is_canceled")
    missing = sorted(required.difference(raw.columns))
    if missing:
        raise ValueError(f"raw bookings are missing required columns: {missing}")

    prepared = raw.copy(deep=True)
    prepared["arrival_date"] = arrival_date(prepared)
    prepared["nights"] = (
        prepared["stays_in_weekend_nights"] + prepared["stays_in_week_nights"]
    )

    prepared["children"] = prepared["children"].fillna(0)
    prepared["country"] = prepared["country"].fillna("Unknown")
    prepared["agent"] = _category_values(prepared["agent"], "No agent")
    prepared["company"] = _category_values(prepared["company"], "No company")

    output_columns: list[str] = list(MODEL_FEATURES)
    for column in ("arrival_date", "nights", "adr", "is_canceled"):
        if column in prepared and (column != "is_canceled" or require_target):
            output_columns.append(column)
    return prepared.loc[:, output_columns].copy()


def model_features(bookings: pd.DataFrame) -> pd.DataFrame:
    """Return only the predictors approved for the MVP."""
    missing = sorted(set(MODEL_FEATURES).difference(bookings.columns))
    if missing:
        raise ValueError(f"bookings are missing model features: {missing}")
    return bookings.loc[:, MODEL_FEATURES].copy()


if __name__ == "__main__":
    print(f"{len(MODEL_FEATURES)} booking-time model features defined")
