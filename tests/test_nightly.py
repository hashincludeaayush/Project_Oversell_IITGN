"""Synthetic tests for the saved-policy nightly MVP."""

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

import nightly  # noqa: E402
from models.baselines import FlatRuleModel  # noqa: E402
from models.classifiers import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERICAL_FEATURES  # noqa: E402
from models.helpers import predict_cancellation_probability  # noqa: E402
from models.persistence import load_selected_policy, save_selected_policy  # noqa: E402


def raw_bookings():
    rows = []
    for arrival in pd.date_range("2017-08-17", periods=16, freq="D"):
        for hotel in ("City Hotel", "Resort Hotel"):
            for guest in range(5):
                rows.append(
                    {
                        "hotel": hotel,
                        "lead_time": 70 + guest * 5,
                        "arrival_date_year": arrival.year,
                        "arrival_date_month": arrival.strftime("%B"),
                        "arrival_date_week_number": arrival.isocalendar().week,
                        "arrival_date_day_of_month": arrival.day,
                        "stays_in_weekend_nights": 1,
                        "stays_in_week_nights": 1,
                        "adults": 2,
                        "children": 0,
                        "babies": 0,
                        "meal": "BB",
                        "country": "PRT",
                        "market_segment": "Online TA" if hotel == "City Hotel" else "Direct",
                        "distribution_channel": "TA/TO",
                        "is_repeated_guest": 0,
                        "previous_cancellations": 0,
                        "previous_bookings_not_canceled": 0,
                        "reserved_room_type": "A",
                        "deposit_type": "No Deposit",
                        "agent": 9,
                        "company": np.nan,
                        "customer_type": "Transient",
                        "adr": 100 + guest,
                        "is_canceled": guest % 2,
                    }
                )
    return pd.DataFrame(rows)


def save_flat_policy(path):
    train = pd.DataFrame(
        {
            "hotel": ["City Hotel", "City Hotel", "Resort Hotel", "Resort Hotel"],
            "is_canceled": [1, 0, 1, 0],
        }
    )
    candidate = {
        "method": "Client Flat Rule",
        "model": FlatRuleModel().fit(train),
        "buffer": 3,
    }
    metrics = {
        "AUC": 0.72,
        "Buffer": 3,
        "Ceiling met": True,
        "Walks/1,000": 8.0,
    }
    return save_selected_policy(candidate, metrics, path)


def test_nightly_loads_saved_policy_filters_and_exports_aligned_recommendations(
    monkeypatch, tmp_path
):
    raw = raw_bookings()
    policy_path = save_flat_policy(tmp_path / "selected_policy.joblib")
    output_path = tmp_path / "exports" / "nightly.csv"
    prepared = nightly.features.prepare_bookings(raw, require_target=False)
    expected_filtered = prepared.loc[
        prepared["arrival_date"].ge(pd.Timestamp("2017-08-18"))
        & prepared["arrival_date"].lt(pd.Timestamp("2017-09-01"))
    ]
    predictor_indexes = []
    loaded_paths = []
    load_policy = nightly.load_selected_policy

    def track_load(path):
        loaded_paths.append(path)
        return load_policy(path)

    def deterministic_predictions(model, model_inputs):
        assert "is_canceled" not in model_inputs
        assert "arrival_date" not in model_inputs
        assert list(model_inputs.index) == list(expected_filtered.index)
        predictor_indexes.extend(model_inputs.index.tolist())
        return model_inputs["lead_time"].to_numpy(dtype=float) / 100.0

    monkeypatch.setattr(nightly, "load_selected_policy", track_load)
    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)
    monkeypatch.setattr(nightly, "predict_cancellation_probability", deterministic_predictions)

    # A fitted estimator and a frozen buffer must be used as-is at inference time.
    monkeypatch.setattr(
        FlatRuleModel,
        "fit",
        lambda *args, **kwargs: pytest.fail("nightly execution must not fit a model"),
    )
    monkeypatch.setattr(
        "models.buffer.find_optimal_buffer",
        lambda *args, **kwargs: pytest.fail("nightly execution must not tune the buffer"),
    )

    recommendations = nightly.run_nightly(
        "2017-08-18",
        14,
        model_path=policy_path,
        output_path=output_path,
    )

    expected_dates = pd.date_range("2017-08-18", periods=14, freq="D").strftime(
        "%Y-%m-%d"
    ).tolist()
    assert loaded_paths == [policy_path]
    assert len(predictor_indexes) == len(expected_filtered)
    assert recommendations["arrival_date"].drop_duplicates().tolist() == expected_dates
    assert recommendations["arrival_date"].min() == "2017-08-18"
    assert recommendations["arrival_date"].max() == "2017-08-31"
    assert set(recommendations["hotel"]) == {"City Hotel", "Resort Hotel"}
    assert recommendations["bookings_on_book"].eq(5).all()
    assert recommendations["actual_cancellations"].eq(2).all()
    assert recommendations["expected_cancellations"].eq(4.0).all()
    assert recommendations["buffer"].eq(3).all()
    assert recommendations["recommended_oversell"].eq(1).all()
    assert recommendations["cancellation_spread"].iloc[0] == pytest.approx(np.sqrt(0.775))
    assert recommendations["stay_value"].eq(204.0).all()
    assert recommendations.columns.tolist() == nightly.OUTPUT_COLUMNS
    assert pd.read_csv(output_path).columns.tolist() == nightly.OUTPUT_COLUMNS


@pytest.mark.parametrize("start_date", ["not-a-date", "2017-02-30", "2017-8-18"])
def test_invalid_start_dates_are_rejected_before_loading(start_date):
    with pytest.raises(ValueError, match="Start date"):
        nightly.run_nightly(start_date, 14)


@pytest.mark.parametrize("nights", [0, -1, 1.5, True])
def test_invalid_night_counts_are_rejected_before_loading(nights):
    with pytest.raises(ValueError, match="Number of nights"):
        nightly.run_nightly("2017-08-18", nights)


def test_missing_and_invalid_policy_artifacts_have_clear_errors(monkeypatch):
    monkeypatch.setattr(
        nightly,
        "load_selected_policy",
        lambda path: (_ for _ in ()).throw(FileNotFoundError(path)),
    )
    with pytest.raises(FileNotFoundError, match="Selected model artifact was not found"):
        nightly.run_nightly("2017-08-18", 14)

    monkeypatch.setattr(
        nightly,
        "load_selected_policy",
        lambda path: (_ for _ in ()).throw(ValueError("invalid schema")),
    )
    with pytest.raises(ValueError, match="Could not load selected model artifact.*invalid schema"):
        nightly.run_nightly("2017-08-18", 14)


def test_empty_arrival_window_is_rejected_without_export(monkeypatch, tmp_path):
    raw = raw_bookings()
    policy_path = save_flat_policy(tmp_path / "selected_policy.joblib")
    output_path = tmp_path / "empty.csv"
    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)

    with pytest.raises(ValueError, match="No bookings arrive"):
        nightly.run_nightly(
            "2018-01-01",
            14,
            model_path=policy_path,
            output_path=output_path,
        )
    assert not output_path.exists()


def test_partially_missing_calendar_date_fails_with_missing_date(monkeypatch, tmp_path):
    raw = raw_bookings()
    raw = raw.loc[raw["arrival_date_day_of_month"] != 23]
    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)
    monkeypatch.setattr(
        nightly,
        "load_selected_policy",
        lambda path: {"model": object(), "buffer": 3},
    )
    monkeypatch.setattr(
        nightly,
        "predict_cancellation_probability",
        lambda model, rows: rows["lead_time"].to_numpy(dtype=float) / 100.0,
    )

    with pytest.raises(ValueError, match="missing arrival dates: 2017-08-23"):
        nightly.run_nightly(
            "2017-08-18",
            14,
            model_path=tmp_path / "synthetic.joblib",
            output_path=tmp_path / "partial.csv",
        )


def test_missing_hotel_date_combination_fails_after_grouping(monkeypatch, tmp_path):
    raw = raw_bookings()
    raw = raw.loc[
        ~(
            raw["hotel"].eq("Resort Hotel")
            & raw["arrival_date_day_of_month"].eq(23)
        )
    ]
    monkeypatch.setattr(nightly.data, "read_raw", lambda: raw)
    monkeypatch.setattr(
        nightly,
        "load_selected_policy",
        lambda path: {"model": object(), "buffer": 3},
    )
    monkeypatch.setattr(
        nightly,
        "predict_cancellation_probability",
        lambda model, rows: rows["lead_time"].to_numpy(dtype=float) / 100.0,
    )

    with pytest.raises(
        ValueError,
        match=r"missing hotel/date combinations: \(Resort Hotel, 2017-08-23\)",
    ):
        nightly.run_nightly(
            "2017-08-18",
            14,
            model_path=tmp_path / "synthetic.joblib",
            output_path=tmp_path / "partial_hotel.csv",
        )


def test_saved_random_forest_pipeline_predicts_on_synthetic_features_in_row_order():
    policy_path = nightly.DEFAULT_MODEL_PATH
    policy = load_selected_policy(policy_path)
    assert policy["method"] == "Random Forest"
    assert policy["buffer"] == 3

    rows = {
        name: [index + offset for offset in range(4)]
        for index, name in enumerate(NUMERICAL_FEATURES)
    }
    for index, name in enumerate(CATEGORICAL_FEATURES):
        rows[name] = [f"category-{index}-{row}" for row in range(4)]
    rows["hotel"] = ["City Hotel", "Resort Hotel", "City Hotel", "Resort Hotel"]
    rows["arrival_date_month"] = ["August"] * 4
    rows["meal"] = ["BB"] * 4
    rows["country"] = ["PRT"] * 4
    rows["market_segment"] = ["Online TA"] * 4
    rows["distribution_channel"] = ["TA/TO"] * 4
    rows["reserved_room_type"] = ["A"] * 4
    rows["deposit_type"] = ["No Deposit"] * 4
    rows["customer_type"] = ["Transient"] * 4
    frame = pd.DataFrame(rows).loc[:, FEATURE_COLUMNS]

    batch_probabilities = predict_cancellation_probability(policy["model"], frame)
    single_row_probabilities = np.asarray(
        [
            predict_cancellation_probability(policy["model"], frame.iloc[[index]])[0]
            for index in range(len(frame))
        ]
    )

    assert batch_probabilities.shape == (len(frame),)
    assert np.isfinite(batch_probabilities).all()
    assert ((batch_probabilities >= 0) & (batch_probabilities <= 1)).all()
    np.testing.assert_allclose(batch_probabilities, single_row_probabilities)


def test_cli_preserves_documented_arguments_and_allows_output_override(tmp_path):
    args = nightly.build_parser().parse_args(
        [
            "--from",
            "2017-08-18",
            "--nights",
            "14",
            "--output",
            str(tmp_path / "recommendations.csv"),
        ]
    )

    assert args.start_date.isoformat() == "2017-08-18"
    assert args.nights == 14
    assert args.output == tmp_path / "recommendations.csv"
