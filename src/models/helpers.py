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

def run_on_proof(candidate: dict, proof) -> dict:
  """Evaluate candidate model on proof using its frozen buffer."""
  model = candidate["model"]
  buffer = candidate["buffer"]
  probabilities = predict_cancellation_probability(model, proof)
  nightly = contract.nightly_table(proof, probabilities)
  metrics = evaluate_buffer(nightly, buffer)
  return {
      "method": candidate["method"],
      "model": model,
      "buffer": buffer,
      "probabilities": probabilities,
      "nights": nightly,
      "metrics": metrics,
  }


def build_comparison_table(period_runs, bookings):
    """Build the same metrics table for a period's scored runs."""
    flat_cost = next(
        run["metrics"]["cost_eur"]
        for run in period_runs
        if run["method"] == "Client Flat Rule"
    )

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