"""Save and load the fitted policy selected on the Choose period."""

from pathlib import Path
from numbers import Real
import math

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

import contract
from models.baselines import FlatRuleModel, LookupTableModel
from models.classifiers import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
)

POLICY_SCHEMA_VERSION = 2
SELECTION_CRITERION = "highest_choose_auc_among_choose_walk_ceiling_compliant"


def _is_simple_value(value):
    if isinstance(value, np.generic):
        value = value.item()
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, (list, tuple)):
        return all(_is_simple_value(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _is_simple_value(item)
            for key, item in value.items()
        )
    return False


def _simple_parameters(estimator):
    parameters = {}
    for name, value in estimator.get_params(deep=True).items():
        if isinstance(value, np.generic):
            value = value.item()
        if _is_simple_value(value):
            parameters[name] = value
    return parameters


def _model_features(method, model):
    if method == "Client Flat Rule" and isinstance(model, FlatRuleModel):
        return ["hotel"]
    if method == "Lookup Table" and isinstance(model, LookupTableModel):
        return ["hotel", "market_segment", "lead_time"]

    classifiers = {
        "Decision Tree": DecisionTreeClassifier,
        "Random Forest": RandomForestClassifier,
        "Logistic Regression": LogisticRegression,
    }
    classifier_type = classifiers.get(method)
    if classifier_type is None:
        raise ValueError(f"Unsupported selected model method: {method!r}.")
    if not isinstance(model, Pipeline):
        raise ValueError(f"Method {method!r} must use a fitted sklearn Pipeline.")

    try:
        estimator = model.named_steps["clf"]
        preprocessor = model.named_steps["prep"]
    except KeyError as exc:
        raise ValueError(f"Method {method!r} pipeline needs 'prep' and 'clf' steps.") from exc
    if not isinstance(estimator, classifier_type):
        raise ValueError(f"Method {method!r} has an incompatible estimator type.")
    if not isinstance(preprocessor, ColumnTransformer):
        raise ValueError(f"Method {method!r} needs a ColumnTransformer preprocessor.")

    columns_by_transformer = {}
    try:
        for name, _, columns in preprocessor.transformers:
            if name in {"num", "cat"}:
                columns_by_transformer[name] = list(columns)
    except TypeError as exc:
        raise ValueError(f"Method {method!r} has invalid preprocessing columns.") from exc

    if columns_by_transformer.get("num") != list(NUMERICAL_FEATURES):
        raise ValueError(f"Method {method!r} numerical preprocessing features do not match.")
    if columns_by_transformer.get("cat") != list(CATEGORICAL_FEATURES):
        raise ValueError(f"Method {method!r} categorical preprocessing features do not match.")
    return list(FEATURE_COLUMNS)


def _is_boolean(value):
    return isinstance(value, (bool, np.bool_))


def _validate_choose_metrics(metrics, buffer):
    if not isinstance(metrics, dict):
        raise ValueError("Choose metrics must be a dictionary.")

    compliant = metrics.get("Ceiling met")
    if not _is_boolean(compliant) or not bool(compliant):
        raise ValueError("Choose metrics must establish Boolean walk-ceiling compliance.")

    walks = metrics.get("Walks/1,000")
    if isinstance(walks, (bool, np.bool_)) or not isinstance(walks, Real):
        raise ValueError("Choose metrics must include a numeric 'Walks/1,000' value.")
    if not math.isfinite(float(walks)) or float(walks) > contract.WALK_CEILING:
        raise ValueError("Choose walks exceed the configured walk ceiling.")

    auc = metrics.get("AUC")
    if isinstance(auc, (bool, np.bool_)) or not isinstance(auc, Real):
        raise ValueError("Choose metrics must include a numeric AUC.")
    if not math.isfinite(float(auc)) or not 0.0 <= float(auc) <= 1.0:
        raise ValueError("Choose AUC must be finite and between 0 and 1.")

    selected_buffer = metrics.get("Buffer")
    if (
        isinstance(selected_buffer, (bool, np.bool_))
        or not isinstance(selected_buffer, (int, np.integer))
        or int(selected_buffer) != int(buffer)
    ):
        raise ValueError("Choose metrics buffer does not match the saved policy buffer.")


def _configuration(candidate):
    model = candidate["model"]
    _model_features(candidate["method"], model)
    model_class = f"{type(model).__module__}.{type(model).__name__}"
    configuration = {
        "class": model_class,
        "parameters": {},
    }
    preprocessing = None

    if isinstance(model, Pipeline):
        estimator = model.named_steps["clf"]
        preprocessor = model.named_steps["prep"]
        configuration["estimator"] = {
            "class": f"{type(estimator).__module__}.{type(estimator).__name__}",
            "parameters": _simple_parameters(estimator),
        }
        preprocessing = {
            "class": f"{type(preprocessor).__module__}.{type(preprocessor).__name__}",
            "parameters": _simple_parameters(preprocessor),
            "numerical_features": list(NUMERICAL_FEATURES),
            "categorical_features": list(CATEGORICAL_FEATURES),
        }
    elif hasattr(model, "get_params"):
        configuration["parameters"] = _simple_parameters(model)

    return configuration, preprocessing


def save_selected_policy(candidate, choose_metrics, path):
    """Persist the fitted Train model and its frozen Choose selection metadata."""
    metrics = dict(choose_metrics)
    buffer = candidate["buffer"]
    if isinstance(buffer, bool) or not isinstance(buffer, (int, np.integer)) or buffer < 0:
        raise ValueError("The selected buffer must be a non-negative integer.")
    _validate_choose_metrics(metrics, buffer)

    model_configuration, preprocessing_configuration = _configuration(candidate)
    feature_columns = _model_features(candidate["method"], candidate["model"])
    policy = {
        "schema_version": POLICY_SCHEMA_VERSION,
        "method": candidate["method"],
        "model": candidate["model"],
        "buffer": int(buffer),
        "feature_columns": feature_columns,
        "model_configuration": model_configuration,
        "preprocessing_configuration": preprocessing_configuration,
        "choose_metrics": metrics,
        "training_period": {"arrival_date_before": contract.TRAIN_END},
        "choose_period": {
            "arrival_date_start_inclusive": contract.TRAIN_END,
            "arrival_date_end_exclusive": contract.PROOF_START,
        },
        "proof_period": {
            "arrival_date_start_inclusive": contract.PROOF_START,
            "expected_dataset_end_inclusive": "2017-08-31",
        },
        "selection_criterion": SELECTION_CRITERION,
        "walk_ceiling_per_1000": contract.WALK_CEILING,
        "buffer_rule": "max(0, round(expected_cancellations - buffer))",
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(policy, path)
    return path


def load_selected_policy(path):
    """Load a persisted policy and validate its frozen selection metadata."""
    policy = joblib.load(path)
    if not isinstance(policy, dict):
        raise ValueError("Selected-policy artifact must contain a dictionary.")

    version = policy.get("schema_version")
    if (
        isinstance(version, (bool, np.bool_))
        or not isinstance(version, (int, np.integer))
        or int(version) != POLICY_SCHEMA_VERSION
    ):
        raise ValueError(f"Unsupported selected-policy schema version: {version!r}.")

    buffer = policy.get("buffer")
    if (
        isinstance(buffer, (bool, np.bool_))
        or not isinstance(buffer, (int, np.integer))
        or int(buffer) < 0
    ):
        raise ValueError("Selected-policy buffer must be a non-negative integer, not Boolean.")

    if "model" not in policy or "method" not in policy:
        raise ValueError("Selected-policy artifact is missing its model or method.")
    _validate_choose_metrics(policy.get("choose_metrics"), buffer)

    if policy.get("selection_criterion") != SELECTION_CRITERION:
        raise ValueError("Selected-policy artifact has an unsupported selection criterion.")
    if policy.get("walk_ceiling_per_1000") != contract.WALK_CEILING:
        raise ValueError("Selected-policy walk ceiling does not match the evaluation contract.")

    expected_features = _model_features(policy["method"], policy["model"])
    feature_columns = policy.get("feature_columns")
    if (
        not isinstance(feature_columns, list)
        or not all(isinstance(name, str) for name in feature_columns)
        or len(feature_columns) != len(set(feature_columns))
        or feature_columns != expected_features
    ):
        raise ValueError("Selected-policy feature columns are missing or inconsistent with its model.")

    if "preprocessing_configuration" not in policy:
        raise ValueError("Selected-policy preprocessing feature metadata is missing.")
    model_configuration = policy.get("model_configuration")
    if not isinstance(model_configuration, dict):
        raise ValueError("Selected-policy model configuration is missing.")
    expected_model_configuration, expected_preprocessing = _configuration(
        {"method": policy["method"], "model": policy["model"]}
    )
    if model_configuration != expected_model_configuration:
        raise ValueError("Selected-policy model configuration is inconsistent with its model.")
    if policy["preprocessing_configuration"] != expected_preprocessing:
        raise ValueError("Selected-policy preprocessing metadata is inconsistent with its model.")

    proof_period = policy.get("proof_period")
    if (
        not isinstance(proof_period, dict)
        or proof_period.get("arrival_date_start_inclusive") != contract.PROOF_START
        or proof_period.get("expected_dataset_end_inclusive") != "2017-08-31"
    ):
        raise ValueError("Selected-policy Proof metadata must label 2017-08-31 as an expected dataset boundary.")
    return policy
