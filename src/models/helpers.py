import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, mean_absolute_error

import contract
from models.baselines import FlatRuleModel, LookupTableModel
from models.buffer import find_optimal_buffer, evaluate_buffer
from models.classifiers import build_decision_tree, build_random_forest, build_logistic_regression, FEATURE_COLUMNS

METHODS = {
    "Client Flat Rule": FlatRuleModel,
    "Lookup Table": LookupTableModel,
    "Decision Tree": build_decision_tree,
    "Random Forest": build_random_forest,
    "Logistic Regression": build_logistic_regression,
}


def fit_candidate(model, train):
    """Fit either a project baseline or a scikit-learn classifier."""
    if hasattr(model, "predict_probability"):
        # Baseline models use the full booking rows.
        model.fit(train)
    else:
        # Classifiers use the audited model features.
        model.fit(train[FEATURE_COLUMNS], train["is_canceled"])
    return model


def predict_cancellation_probability(model, bookings):
    """Return one cancellation probability per booking."""
    if hasattr(model, "predict_probability"):
        return model.predict_probability(bookings)

    return model.predict_proba(bookings[FEATURE_COLUMNS])[:, 1]


def run_on_choose(name, model_factory, train, choose):
    """Fit on train; choose the buffer and record results on choose."""
    model = fit_candidate(model_factory(), train)
    probabilities = predict_cancellation_probability(model, choose)
    nightly = contract.nightly_table(choose, probabilities)
    buffer, metrics = find_optimal_buffer(nightly)
    return {
        "method": name,
        "model": model,
        "buffer": buffer,
        "probabilities": probabilities,
        "nights": nightly,
        "metrics": metrics,
    }

def _score_candidate(candidate: dict, bookings) -> dict:
    """Score a fitted candidate on a period using its already chosen buffer."""
    model = candidate["model"]
    buffer = candidate["buffer"]
    probabilities = predict_cancellation_probability(model, bookings)
    nightly = contract.nightly_table(bookings, probabilities)
    metrics = evaluate_buffer(nightly, buffer)
    return {
        "method": candidate["method"],
        "model": model,
        "buffer": buffer,
        "probabilities": probabilities,
        "nights": nightly,
        "metrics": metrics,
    }


def run_on_proof(candidate: dict, proof) -> dict:
    """Evaluate the frozen winner on proof using its frozen buffer."""
    return _score_candidate(candidate, proof)


def score_flat_rule_reference(candidate: dict, proof) -> dict:
    """Score the frozen client baseline on proof for the required cost comparison."""
    if candidate["method"] != "Client Flat Rule":
        raise ValueError("The proof reference must be the Client Flat Rule candidate.")
    return _score_candidate(candidate, proof)


def select_winner(choose_results, choose_table):
    """Return the highest-AUC candidate that meets the Choose walk ceiling."""
    required = {"Method", "AUC", "Ceiling met"}
    missing = required.difference(choose_table.columns)
    if missing:
        raise ValueError(f"Choose comparison is missing columns: {sorted(missing)}")

    ceiling_flags = choose_table["Ceiling met"]
    invalid_flags = [
        value
        for value in ceiling_flags
        if not isinstance(value, (bool, np.bool_))
    ]
    if invalid_flags:
        raise ValueError("Choose comparison 'Ceiling met' must contain only Boolean values.")

    eligible = choose_table.loc[
        ceiling_flags.map(bool) & choose_table["AUC"].notna()
    ]
    if eligible.empty:
        raise ValueError("No candidate policy meets the walk ceiling on Choose.")

    winner_row = eligible.loc[eligible["AUC"].idxmax()]
    winner = next(
        (candidate for candidate in choose_results if candidate["method"] == winner_row["Method"]),
        None,
    )
    if winner is None:
        raise ValueError(
            f"Selected method {winner_row['Method']!r} has no matching fitted candidate."
        )
    return winner, winner_row.to_dict()


def build_comparison_table(period_runs, bookings, *, flat_cost=None):
    """Build the same metrics table for a period's scored runs."""
    if flat_cost is None:
        flat_run = next(
            (run for run in period_runs if run["method"] == "Client Flat Rule"),
            None,
        )
        if flat_run is None:
            raise ValueError("A flat-rule cost is required to build the comparison table.")
        flat_cost = flat_run["metrics"]["cost_eur"]

    rows = []
    for run in period_runs:
        metrics = run["metrics"]
        nights = run["nights"]

        rows.append({
            "Method": run["method"],
            "Buffer": run["buffer"],
            "AUC": roc_auc_score(
                bookings["is_canceled"],
                run["probabilities"],
            ),
            "MAE": mean_absolute_error(
                nights["cancelled"],
                nights["expected"],
            ),
            "Empty rooms": metrics["empty_rooms"],
            "Walked guests": metrics["walked_guests"],
            "Walks/1,000": metrics["walks_per_1000"],
            "Cost (€)": metrics["cost_eur"],
            "Savings (€)": flat_cost - metrics["cost_eur"],
            "Ceiling met": metrics["ceiling_met"],
        })

    return pd.DataFrame(rows)
