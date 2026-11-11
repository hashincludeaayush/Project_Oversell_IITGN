"""Focused tests for the Data Lead's feature-preparation contract."""

import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import features  # noqa: E402


def raw_rows():
    return pd.DataFrame(
        {
            "hotel": ["City Hotel", "Resort Hotel"],
            "lead_time": [10, 20],
            "arrival_date_year": [2017, 2017],
            "arrival_date_month": ["August", "August"],
            "arrival_date_day_of_month": [18, 19],
            "arrival_date_week_number": [33, 33],
            "stays_in_weekend_nights": [1, 0],
            "stays_in_week_nights": [2, 1],
            "adults": [2, 1],
            "children": [float("nan"), 0],
            "babies": [0, 0],
            "meal": ["BB", "HB"],
            "country": [float("nan"), "PRT"],
            "market_segment": ["Online TA", "Direct"],
            "distribution_channel": ["TA/TO", "Direct"],
            "is_repeated_guest": [0, 0],
            "previous_cancellations": [0, 0],
            "previous_bookings_not_canceled": [0, 1],
            "reserved_room_type": ["A", "B"],
            "deposit_type": ["No Deposit", "No Deposit"],
            "agent": [float("nan"), 9],
            "company": [float("nan"), float("nan")],
            "customer_type": ["Transient", "Transient"],
            "adr": [100.0, 120.0],
            "is_canceled": [0, 1],
        }
    )


def test_prepare_bookings_derives_dates_and_documents_missing_categories():
    raw = raw_rows()
    prepared = features.prepare_bookings(raw)

    assert prepared["arrival_date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2017-08-18",
        "2017-08-19",
    ]
    assert prepared["nights"].tolist() == [3, 1]
    assert prepared["children"].tolist() == [0, 0]
    assert prepared["country"].tolist() == ["Unknown", "PRT"]
    assert prepared["agent"].tolist() == ["No agent", "9"]
    assert prepared["company"].tolist() == ["No company", "No company"]
    assert raw["children"].isna().any()


def test_model_features_exclude_outcomes_and_late_columns():
    assert not set(features.MODEL_FEATURES).intersection(
        features.FORBIDDEN_MODEL_COLUMNS
    )
    prepared = features.prepare_bookings(raw_rows())
    predictors = features.model_features(prepared)
    assert list(predictors.columns) == list(features.MODEL_FEATURES)
    assert "is_canceled" not in predictors
    assert "reservation_status" not in predictors


def test_prepare_bookings_can_prepare_prediction_rows_without_target():
    raw = raw_rows().drop(columns="is_canceled")
    prepared = features.prepare_bookings(raw, require_target=False)
    assert "is_canceled" not in prepared
    assert "arrival_date" in prepared and "nights" in prepared


def test_missing_required_column_is_rejected():
    with pytest.raises(ValueError, match="missing required columns"):
        features.prepare_bookings(raw_rows().drop(columns="hotel"))
