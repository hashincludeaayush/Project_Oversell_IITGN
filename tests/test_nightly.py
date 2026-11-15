
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Ensure src is importable even when this test file runs independently.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import nightly


def raw_bookings(include_target=True):
    """Create synthetic bookings covering 16 days and both hotels."""

    rows = []

    for arrival in pd.date_range("2017-08-18", periods=16, freq="D"):
        for hotel in ["City Hotel", "Resort Hotel"]:
            for guest in range(5):
                row = {
                    "hotel": hotel,
                    "lead_time": 40,
                    "arrival_date_year": 2017,
                    "arrival_date_month": arrival.strftime("%B"),
                    "arrival_date_week_number": arrival.isocalendar().week,
                    "arrival_date_day_of_month": arrival.day,
                    "stays_in_weekend_nights": 1,
                    "stays_in_week_nights": 2,
                    "adults": 2,
                    "children": 0,
                    "babies": 0,
                    "meal": "BB",
                    "country": "PRT",
                    "market_segment": "Online TA",
                    "distribution_channel": "TA/TO",
                    "is_repeated_guest": 0,
                    "previous_cancellations": 0,
                    "previous_bookings_not_canceled": 0,
                    "reserved_room_type": "A",
                    "assigned_room_type": "A",
                    "booking_changes": 0,
                    "deposit_type": "No Deposit",
                    "agent": 1,
                    "company": np.nan,
                    "days_in_waiting_list": 0,
                    "customer_type": "Transient",
                    "adr": 100.0,
                    "required_car_parking_spaces": 0,
                    "total_of_special_requests": 0,
                    "reservation_status": "Check-Out",
                    "reservation_status_date": arrival,
                    "arrival_date": arrival,
                }

                if include_target:
                    row["is_canceled"] = 1 if guest < 2 else 0

                rows.append(row)

    return pd.DataFrame(rows)


def mock_frozen_policy(monkeypatch, model_path=None, buffer=3):
    """Provide a frozen policy without creating a fake persistence artifact."""

    policy = {
        "model": object(),
        "buffer": buffer,
    }

    loaded_paths = []

    def fake_load_policy(path):
        loaded_paths.append(path)
        return policy

    monkeypatch.setattr(nightly, "_load_policy", fake_load_policy)

    return policy, loaded_paths


def deterministic_predictions(model, model_inputs):
    """Return deterministic probabilities for pipeline tests."""

    assert "is_canceled" not in model_inputs.columns
    assert "arrival_date" not in model_inputs.columns

    return model_inputs["lead_time"].to_numpy(dtype=float) / 100.0


def test_nightly_loads_saved_policy_filters_and_exports_aligned_recommendations(
    monkeypatch, tmp_path
):
    raw = raw_bookings()
    policy_path = tmp_path / "selected_policy.joblib"
    output_path = tmp_path / "exports" / "nightly.csv"

    prepared = nightly.features.prepare_bookings(
        raw,
        require_target=False,
    )

    expected_filtered = prepared.loc[
        prepared["arrival_date"].ge(pd.Timestamp("2017-08-18"))
        & prepared["arrival_date"].lt(pd.Timestamp("2017-09-01"))
    ]

    policy, loaded_paths = mock_frozen_policy(
        monkeypatch,
        model_path=policy_path,
        buffer=3,
    )

    predictor_indexes = []

    def tracked_predictions(model, model_inputs):
        assert model is policy["model"]
        assert "is_canceled" not in model_inputs.columns
        assert "arrival_date" not in model_inputs.columns
        assert list(model_inputs.index) == list(expected_filtered.index)

        predictor_indexes.extend(model_inputs.index.tolist())

        return deterministic_predictions(model, model_inputs)

    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)

    monkeypatch.setattr(
        nightly,
        "predict_cancellation_probability",
        tracked_predictions,
    )

    recommendations = nightly.run_nightly(
        "2017-08-18",
        14,
        model_path=policy_path,
        output_path=output_path,
    )

    expected_dates = pd.date_range(
        "2017-08-18",
        periods=14,
        freq="D",
    ).strftime("%Y-%m-%d").tolist()

    assert loaded_paths == [policy_path]
    assert len(predictor_indexes) == len(expected_filtered)

    assert recommendations["arrival_date"].drop_duplicates().tolist() == expected_dates
    assert recommendations["arrival_date"].min() == "2017-08-18"
    assert recommendations["arrival_date"].max() == "2017-08-31"

    assert set(recommendations["hotel"]) == {
        "City Hotel",
        "Resort Hotel",
    }

    assert recommendations["bookings_on_book"].eq(5).all()
    assert recommendations["expected_cancellations"].eq(2.0).all()
    assert recommendations["buffer"].eq(3).all()
    assert recommendations["recommended_oversell"].eq(0).all()

    assert recommendations.columns.tolist() == nightly.OUTPUT_COLUMNS

    assert "actual_cancellations" not in recommendations.columns
    assert "cancellation_spread" not in recommendations.columns
    assert "stay_value" not in recommendations.columns

    assert output_path.exists()

    saved = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(saved, recommendations)


def test_nightly_does_not_require_actual_cancellation_target(
    monkeypatch, tmp_path
):
    raw = raw_bookings(include_target=False)
    policy, _ = mock_frozen_policy(monkeypatch, buffer=3)

    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)
    monkeypatch.setattr(
        nightly,
        "predict_cancellation_probability",
        deterministic_predictions,
    )

    recommendations = nightly.run_nightly(
        "2017-08-18",
        14,
        output_path=tmp_path / "nightly.csv",
    )

    assert not recommendations.empty
    assert "actual_cancellations" not in recommendations.columns
    assert recommendations.columns.tolist() == nightly.OUTPUT_COLUMNS


@pytest.mark.parametrize(
    "start_date",
    [
        "not-a-date",
        "",
        None,
    ],
)
def test_invalid_start_dates_are_rejected(start_date):
    with pytest.raises(ValueError):
        nightly.parse_start_date(start_date)


@pytest.mark.parametrize(
    "nights",
    [
        0,
        -1,
        1.5,
        "fourteen",
        True,
    ],
)
def test_invalid_night_counts_are_rejected(nights):
    with pytest.raises(ValueError):
        nightly._validate_nights(nights)


def test_missing_policy_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        nightly._load_policy(tmp_path / "missing.joblib")


def test_invalid_policy_file_is_rejected(tmp_path):
    policy_path = tmp_path / "invalid.joblib"
    policy_path.write_text("not a valid policy")

    with pytest.raises(ValueError):
        nightly._load_policy(policy_path)


def test_empty_arrival_window_is_rejected(monkeypatch, tmp_path):
    raw = raw_bookings()
    mock_frozen_policy(monkeypatch)

    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)

    with pytest.raises(ValueError, match="No bookings arrive"):
        nightly.run_nightly(
            "2020-01-01",
            14,
            output_path=tmp_path / "nightly.csv",
        )


def test_missing_date_fails_with_missing_date(monkeypatch, tmp_path):
    raw = raw_bookings()

    missing_date = pd.Timestamp("2017-08-20")
    raw = raw.loc[raw["arrival_date"] != missing_date]

    mock_frozen_policy(monkeypatch)

    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)
    monkeypatch.setattr(
        nightly,
        "predict_cancellation_probability",
        deterministic_predictions,
    )

    with pytest.raises(ValueError, match="2017-08-20"):
        nightly.run_nightly(
            "2017-08-18",
            14,
            output_path=tmp_path / "nightly.csv",
        )


def test_missing_hotel_date_combination_fails_after_grouping(
    monkeypatch, tmp_path
):
    raw = raw_bookings()

    raw = raw.loc[
        ~(
            (raw["hotel"] == "Resort Hotel")
            & (raw["arrival_date"] == pd.Timestamp("2017-08-20"))
        )
    ]

    mock_frozen_policy(monkeypatch)

    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)
    monkeypatch.setattr(
        nightly,
        "predict_cancellation_probability",
        deterministic_predictions,
    )

    with pytest.raises(ValueError, match="missing hotel/date combinations"):
        nightly.run_nightly(
            "2017-08-18",
            14,
            output_path=tmp_path / "nightly.csv",
        )


def test_saved_random_forest_policy_loads_and_predicts():
    model_path = PROJECT_ROOT / "models" / "selected_policy.joblib"

    if not model_path.exists():
        pytest.skip("Committed selected policy artifact is unavailable")

    policy = nightly.load_selected_policy(model_path)

    assert policy["buffer"] == 3
    assert policy["model"] is not None

    raw = raw_bookings()

    prepared = nightly.features.prepare_bookings(
        raw,
        require_target=False,
    )

    model_inputs = nightly.features.model_features(prepared)

    predictions = nightly.predict_cancellation_probability(
        policy["model"],
        model_inputs,
    )

    assert len(predictions) == len(prepared)
    assert np.isfinite(predictions).all()
    assert ((predictions >= 0) & (predictions <= 1)).all()


def test_cli_arguments_are_available():
    parser = nightly.build_parser()

    args = parser.parse_args(
        [
            "--from",
            "2017-08-18",
            "--nights",
            "14",
        ]
    )

    assert args.start_date == date(2017, 8, 18)
    assert args.nights == 14
