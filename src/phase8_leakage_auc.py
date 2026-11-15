"""Run the Phase 8 leakage and split-sensitivity experiment."""

from __future__ import annotations

import pathlib
import sys

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import contract
import data
import features


ROOT = pathlib.Path(__file__).resolve().parent.parent
def _pipeline(columns: list[str], frame: pd.DataFrame) -> Pipeline:
    numeric = [
        column
        for column in columns
        if pd.api.types.is_numeric_dtype(frame[column])
    ]
    categorical = [column for column in columns if column not in numeric]
    preprocess = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                numeric,
            ),
            (
                "categorical",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("encode", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocess),
            ("classifier", LogisticRegression(max_iter=500, random_state=42)),
        ]
    )


def _auc(
    model: Pipeline,
    train: pd.DataFrame,
    test: pd.DataFrame,
    columns: list[str],
) -> float:
    model.fit(train[columns], train["is_canceled"])
    probability = model.predict_proba(test[columns])[:, 1]
    return float(roc_auc_score(test["is_canceled"], probability))


def run_experiment() -> pd.DataFrame:
    """Return AUC results for valid, leaked, and random-split runs."""
    raw = data.read_raw()
    prepared = features.prepare_bookings(raw)
    train, _, proof = contract.split_periods(prepared)

    valid_columns = list(features.MODEL_FEATURES)
    valid_train_auc = _auc(
        _pipeline(valid_columns, prepared), train, proof, valid_columns
    )

    leaked = raw.copy()
    leaked_columns = [column for column in leaked.columns if column != "is_canceled"]
    leaked_train_auc = _auc(
        _pipeline(leaked_columns, leaked),
        leaked.loc[train.index],
        leaked.loc[proof.index],
        leaked_columns,
    )

    random_train, random_test = train_test_split(
        prepared,
        test_size=0.2,
        random_state=42,
        stratify=prepared["is_canceled"],
    )
    random_auc = _auc(
        _pipeline(valid_columns, prepared), random_train, random_test, valid_columns
    )

    return pd.DataFrame(
        [
            {
                "run": "A",
                "features": "Bin 1 only",
                "split": "Chronological train/proof",
                "auc": valid_train_auc,
                "trust": "Primary MVP evidence",
            },
            {
                "run": "B",
                "features": "All non-target raw columns",
                "split": "Chronological train/proof",
                "auc": leaked_train_auc,
                "trust": "Diagnostic only; leakage",
            },
            {
                "run": "C",
                "features": "Bin 1 only",
                "split": "Random 80/20",
                "auc": random_auc,
                "trust": "Sensitivity check; not primary evidence",
            },
        ]
    )


if __name__ == "__main__":
    results = run_experiment()
    print(results.to_string(index=False, formatters={"auc": "{:.4f}".format}))
