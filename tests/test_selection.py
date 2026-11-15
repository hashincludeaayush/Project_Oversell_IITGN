"""Focused tests for Choose selection, frozen policy persistence, and Proof ordering."""

import pathlib
import sys

import numpy as np
import pandas as pd
import pytest
import joblib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

import backtest  # noqa: E402
import contract  # noqa: E402
from models.baselines import FlatRuleModel  # noqa: E402
from models.buffer import NoCompliantBufferError, find_optimal_buffer  # noqa: E402
from models.classifiers import (  # noqa: E402
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
    build_decision_tree,
)
from models.helpers import select_winner  # noqa: E402
from models.persistence import (  # noqa: E402
    POLICY_SCHEMA_VERSION,
    SELECTION_CRITERION,
    _model_features,
    load_selected_policy,
    save_selected_policy,
)


def valid_flat_policy(tmp_path):
    path = tmp_path / "valid_policy.joblib"
    save_selected_policy(
        {
            "method": "Client Flat Rule",
            "model": FlatRuleModel(),
            "buffer": 3,
        },
        {
            "AUC": 0.72,
            "Buffer": 3,
            "Ceiling met": True,
            "Walks/1,000": 8.0,
        },
        path,
    )
    return path


def load_modified_policy(tmp_path, update):
    path = valid_flat_policy(tmp_path)
    policy = joblib.load(path)
    update(policy)
    joblib.dump(policy, path)
    return load_selected_policy(path)


def test_selection_uses_choose_auc_and_ignores_proof_metrics():
    candidates = [
        {"method": "Random Forest", "buffer": 3},
        {"method": "Logistic Regression", "buffer": 1},
    ]
    choose_table = pd.DataFrame(
        [
            {"Method": "Random Forest", "AUC": 0.82, "Ceiling met": True, "Proof AUC": 0.70},
            {"Method": "Logistic Regression", "AUC": 0.81, "Ceiling met": True, "Proof AUC": 0.99},
        ]
    )

    winner, row = select_winner(candidates, choose_table)

    assert winner["method"] == "Random Forest"
    assert row["AUC"] == pytest.approx(0.82)


def test_noncompliant_choose_candidate_cannot_win():
    candidates = [
        {"method": "Compliant", "buffer": 2},
        {"method": "Over ceiling", "buffer": 0},
    ]
    choose_table = pd.DataFrame(
        [
            {"Method": "Compliant", "AUC": 0.80, "Ceiling met": True},
            {"Method": "Over ceiling", "AUC": 0.99, "Ceiling met": False},
        ]
    )

    winner, _ = select_winner(candidates, choose_table)

    assert winner["method"] == "Compliant"


def test_no_compliant_choose_candidate_fails_explicitly():
    candidates = [{"method": "Over ceiling", "buffer": 0}]
    choose_table = pd.DataFrame(
        [{"Method": "Over ceiling", "AUC": 0.99, "Ceiling met": False}]
    )

    with pytest.raises(ValueError, match="No candidate policy meets the walk ceiling on Choose"):
        select_winner(candidates, choose_table)


@pytest.mark.parametrize("invalid_flag", ["False", "yes", 1, None])
def test_selection_rejects_non_boolean_ceiling_values(invalid_flag):
    candidates = [{"method": "Candidate"}]
    choose_table = pd.DataFrame(
        [{"Method": "Candidate", "AUC": 0.8, "Ceiling met": invalid_flag}]
    )

    with pytest.raises(ValueError, match="must contain only Boolean values"):
        select_winner(candidates, choose_table)


def test_buffer_search_does_not_fall_back_to_noncompliant_policy():
    nights = pd.DataFrame(
        {
            "expected": [2.0],
            "cancelled": [0],
            "book": [2],
            "stay_value": [100.0],
        }
    )

    with pytest.raises(NoCompliantBufferError, match="No buffer"):
        find_optimal_buffer(nights, min_buffer=0, max_buffer=0)


def test_choose_stage_discards_noncompliant_candidates_and_freezes_winner(monkeypatch, tmp_path):
    calls = []
    candidates = {
        "Client Flat Rule": {"method": "Client Flat Rule", "model": object(), "buffer": 4},
        "Over ceiling": {"method": "Over ceiling", "model": object(), "buffer": 0},
        "Random Forest": {"method": "Random Forest", "model": object(), "buffer": 3},
    }

    def fake_run_on_choose(name, factory, train, choose):
        calls.append(name)
        if name == "Over ceiling":
            raise NoCompliantBufferError("test policy exceeded the Choose walk ceiling")
        return candidates[name]

    def fake_table(results, bookings):
        return pd.DataFrame(
            [
                {"Method": "Client Flat Rule", "AUC": 0.55, "Ceiling met": True},
                {"Method": "Random Forest", "AUC": 0.82, "Ceiling met": True},
            ]
        )

    saved = {}

    def fake_save(candidate, metrics, path):
        saved.update(candidate=candidate, metrics=metrics)
        return path

    def fake_load(path):
        return {**saved["candidate"], "loaded_from": path}

    monkeypatch.setattr(backtest, "run_on_choose", fake_run_on_choose)
    monkeypatch.setattr(backtest, "build_comparison_table", fake_table)
    monkeypatch.setattr(backtest, "save_selected_policy", fake_save)
    monkeypatch.setattr(backtest, "load_selected_policy", fake_load)
    monkeypatch.setattr(
        backtest,
        "run_on_proof",
        lambda *args: pytest.fail("Choose selection must finish before Proof evaluation"),
    )

    selection = backtest.choose_and_freeze(
        pd.DataFrame(),
        pd.DataFrame(),
        methods={name: object for name in candidates},
        policy_path=tmp_path / "selected.joblib",
    )

    assert calls == ["Client Flat Rule", "Over ceiling", "Random Forest"]
    assert selection["winner"]["method"] == "Random Forest"
    assert selection["frozen_policy"]["loaded_from"] == tmp_path / "selected.joblib"
    assert selection["frozen_policy"]["buffer"] == 3
    assert selection["discarded"] == {
        "Over ceiling": "test policy exceeded the Choose walk ceiling"
    }
    assert saved["metrics"]["AUC"] == pytest.approx(0.82)


def test_choose_stage_fails_when_every_candidate_is_noncompliant(monkeypatch, tmp_path):
    def no_compliant_candidate(*args):
        raise NoCompliantBufferError("no compliant buffer")

    monkeypatch.setattr(backtest, "run_on_choose", no_compliant_candidate)

    with pytest.raises(ValueError, match="No candidate policy meets the walk ceiling on Choose"):
        backtest.choose_and_freeze(
            pd.DataFrame(),
            pd.DataFrame(),
            methods={"Only candidate": object},
            policy_path=tmp_path / "unused.joblib",
        )


def test_choose_stage_requires_contract_flat_rule_reference(monkeypatch, tmp_path):
    monkeypatch.setattr(
        backtest,
        "run_on_choose",
        lambda name, *args: {"method": name, "model": object(), "buffer": 1},
    )

    with pytest.raises(ValueError, match="requires a compliant Client Flat Rule baseline"):
        backtest.choose_and_freeze(
            pd.DataFrame(),
            pd.DataFrame(),
            methods={"Random Forest": object},
            policy_path=tmp_path / "unused.joblib",
        )


def test_proof_candidate_evaluation_receives_only_frozen_winner(monkeypatch):
    frozen = {"method": "Random Forest", "buffer": 3, "model": object()}
    proof = pd.DataFrame({"marker": ["proof"]})
    calls = []
    baseline_calls = []

    def fake_run_on_proof(candidate, rows):
        calls.append((candidate, rows))
        return {
            "method": candidate["method"],
            "buffer": candidate["buffer"],
            "probabilities": np.array([0.4, 0.6]),
            "nights": pd.DataFrame({"cancelled": [1], "expected": [1.0]}),
            "metrics": {"cost_eur": 150.0},
        }

    def fake_flat_reference(candidate, rows):
        baseline_calls.append((candidate, rows))
        return {"metrics": {"cost_eur": 200.0}}

    monkeypatch.setattr(backtest, "run_on_proof", fake_run_on_proof)
    monkeypatch.setattr(backtest, "score_flat_rule_reference", fake_flat_reference)
    monkeypatch.setattr(
        backtest,
        "build_comparison_table",
        lambda runs, rows, *, flat_cost: pd.DataFrame(
            [{"Method": runs[0]["method"], "Savings": flat_cost - runs[0]["metrics"]["cost_eur"]}]
        ),
    )

    winner_result, proof_table = backtest.evaluate_frozen_policy(
        {"frozen_policy": frozen, "flat_candidate": {"method": "Client Flat Rule"}},
        proof,
    )

    assert len(calls) == 1
    assert calls[0][0] is frozen
    assert calls[0][1] is proof
    assert len(baseline_calls) == 1
    assert proof_table.iloc[0]["Method"] == "Random Forest"
    assert proof_table.iloc[0]["Savings"] == pytest.approx(50.0)
    assert winner_result["buffer"] == 3


def test_saved_policy_round_trips_fitted_model_and_frozen_settings(tmp_path):
    rows = pd.DataFrame(
        {
            name: [index, index + 1, index + 2, index + 3]
            for index, name in enumerate(NUMERICAL_FEATURES)
        }
    )
    for index, name in enumerate(CATEGORICAL_FEATURES):
        rows[name] = [f"a{index}", f"b{index}", f"a{index}", f"b{index}"]
    labels = np.array([0, 1, 0, 1])
    model = build_decision_tree(max_depth=3, min_samples_leaf=1)
    model.fit(rows[FEATURE_COLUMNS], labels)
    candidate = {
        "method": "Decision Tree",
        "model": model,
        "buffer": 2,
        "metrics": {"ceiling_met": True},
    }
    choose_metrics = {
        "AUC": 0.75,
        "Buffer": 2,
        "Ceiling met": True,
        "Walks/1,000": 8.0,
    }
    path = tmp_path / "selected_policy.joblib"

    saved_path = save_selected_policy(candidate, choose_metrics, path)
    loaded = load_selected_policy(saved_path)

    assert loaded["method"] == "Decision Tree"
    assert loaded["buffer"] == 2
    assert loaded["choose_metrics"]["AUC"] == pytest.approx(0.75)
    assert loaded["choose_metrics"]["Buffer"] == 2
    assert loaded["walk_ceiling_per_1000"] == contract.WALK_CEILING
    assert loaded["feature_columns"] == FEATURE_COLUMNS
    assert loaded["model_configuration"]["estimator"]["parameters"]["max_depth"] == 3
    assert loaded["preprocessing_configuration"]["numerical_features"] == NUMERICAL_FEATURES
    assert loaded["selection_criterion"] == SELECTION_CRITERION
    assert loaded["proof_period"]["expected_dataset_end_inclusive"] == "2017-08-31"
    assert "arrival_date_end_inclusive" not in loaded["proof_period"]
    np.testing.assert_allclose(
        loaded["model"].predict_proba(rows[FEATURE_COLUMNS]),
        model.predict_proba(rows[FEATURE_COLUMNS]),
    )


@pytest.mark.parametrize("bad_version", [True, POLICY_SCHEMA_VERSION + 1, "2"])
def test_loader_rejects_invalid_schema_version(tmp_path, bad_version):
    with pytest.raises(ValueError, match="schema version"):
        load_modified_policy(
            tmp_path,
            lambda policy: policy.update(schema_version=bad_version),
        )


@pytest.mark.parametrize("bad_buffer", [True, False, -1, 1.5])
def test_loader_rejects_invalid_buffer(tmp_path, bad_buffer):
    with pytest.raises(ValueError, match="non-negative integer"):
        load_modified_policy(
            tmp_path,
            lambda policy: policy.update(buffer=bad_buffer),
        )


@pytest.mark.parametrize(
    "bad_metrics",
    [
        {"Ceiling met": "True", "Walks/1,000": 8.0, "AUC": 0.72, "Buffer": 3},
        {"Ceiling met": False, "Walks/1,000": 8.0, "AUC": 0.72, "Buffer": 3},
        {"Ceiling met": True, "Walks/1,000": 10.01, "AUC": 0.72, "Buffer": 3},
        {"Ceiling met": True, "Walks/1,000": "8.0", "AUC": 0.72, "Buffer": 3},
        {"Ceiling met": True, "Walks/1,000": 8.0, "AUC": 0.72, "Buffer": 2},
    ],
)
def test_loader_requires_choose_metrics_to_prove_compliance(tmp_path, bad_metrics):
    with pytest.raises(ValueError, match="Choose"):
        load_modified_policy(
            tmp_path,
            lambda policy: policy.update(choose_metrics=bad_metrics),
        )


def test_loader_rejects_wrong_selection_criterion(tmp_path):
    with pytest.raises(ValueError, match="selection criterion"):
        load_modified_policy(
            tmp_path,
            lambda policy: policy.update(selection_criterion="proof_auc"),
        )


@pytest.mark.parametrize(
    "update",
    [
        lambda policy: policy.pop("feature_columns"),
        lambda policy: policy.update(feature_columns=["lead_time"]),
        lambda policy: policy.pop("preprocessing_configuration"),
        lambda policy: policy.update(model_configuration={"class": "wrong.Model"}),
        lambda policy: policy.update(
            proof_period={
                "arrival_date_start_inclusive": contract.PROOF_START,
                "arrival_date_end_inclusive": "2017-08-31",
            }
        ),
    ],
)
def test_loader_rejects_missing_or_inconsistent_metadata(tmp_path, update):
    with pytest.raises(ValueError):
        load_modified_policy(tmp_path, update)


def test_model_features_reject_unknown_model_types():
    with pytest.raises(ValueError, match="Unsupported selected model method"):
        _model_features("Mystery Model", object())
