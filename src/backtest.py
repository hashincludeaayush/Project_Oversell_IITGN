from sklearn.metrics import roc_auc_score, mean_absolute_error

import contract
import data
import features
from models.baselines import FlatRuleModel, LookupTableModel
from models.buffer import find_optimal_buffer, evaluate_buffer
from models.classifiers import build_decision_tree, FEATURE_COLUMNS, build_random_forest, build_logistic_regression

raw = data.read_raw()
prepared_df = features.prepare_bookings(raw)
train, choose, proof = contract.split_periods(prepared_df)
# Baseline Flat Rule

flatrule_model = FlatRuleModel().fit(train)

# Choose
prob_choose_flat = flatrule_model.predict_probability(choose)
nights_choose_df = contract.nightly_table(choose, prob_choose_flat)
best_flat_buffer, _ = find_optimal_buffer(nights_choose_df)

# Proof
prob_proof_flat = flatrule_model.predict_probability(proof)
nights_proof_df = contract.nightly_table(proof, prob_proof_flat)
res_flat_rule = evaluate_buffer(nights_proof_df, best_flat_buffer)


# Baseline Lookup
lookup_model = LookupTableModel().fit(train)

# Choose
prob_choose_lookup = lookup_model.predict_probability(choose)
nights_choose_lookup = contract.nightly_table(choose, prob_choose_lookup)
best_lookup_buffer, _ = find_optimal_buffer(nights_choose_lookup)

# Proof
prob_proof_lookup = lookup_model.predict_probability(proof)
nights_proof_lookup = contract.nightly_table(proof, prob_proof_lookup)
res_lookup_rule = evaluate_buffer(nights_proof_lookup, best_lookup_buffer)

# ML models Decision Tree

dt_pipeline = build_decision_tree()
dt_pipeline.fit(train[FEATURE_COLUMNS], train["is_canceled"])
prob_choose_dt = dt_pipeline.predict_proba(choose[FEATURE_COLUMNS])[:, 1]
nights_choose_dt = contract.nightly_table(choose, prob_choose_dt)
buf_dt, _ = find_optimal_buffer(nights_choose_dt)

prob_proof_dt = dt_pipeline.predict_proba(proof[FEATURE_COLUMNS])[:, 1]
nights_proof_dt = contract.nightly_table(proof, prob_proof_dt)
res_dt = evaluate_buffer(nights_proof_dt, buf_dt)

# ML models Random Forest

rf_pipeline = build_random_forest()
rf_pipeline.fit(train[FEATURE_COLUMNS], train["is_canceled"])
prob_choose_rf = rf_pipeline.predict_proba(choose[FEATURE_COLUMNS])[:, 1]
nights_choose_rf = contract.nightly_table(choose, prob_choose_rf)
buf_rf, _ = find_optimal_buffer(nights_choose_rf)

prob_proof_rf = rf_pipeline.predict_proba(proof[FEATURE_COLUMNS])[:, 1]
night_proof_rf = contract.nightly_table(proof, prob_proof_rf)
res_rf = evaluate_buffer(night_proof_rf, buf_rf)

# ML models Logistic Regression

lr_pipeline = build_logistic_regression()
lr_pipeline.fit(train[FEATURE_COLUMNS], train["is_canceled"])
prob_choose_lr = lr_pipeline.predict_proba(choose[FEATURE_COLUMNS])[:, 1]
nights_choose_lr = contract.nightly_table(choose, prob_choose_lr)
buf_lr, _ = find_optimal_buffer(nights_choose_lr)

prob_proof_lr = lr_pipeline.predict_proba(proof[FEATURE_COLUMNS])[:, 1]
night_proof_lr = contract.nightly_table(proof, prob_proof_lr)
res_lr = evaluate_buffer(night_proof_lr, buf_lr)

# Comparison Table


flat_cost = res_flat_rule["cost_eur"]
models_data = [
    {
        "Method": "Client Flat Rule",
        "Buffer": best_flat_buffer,
        "AUC": roc_auc_score(proof["is_canceled"], prob_proof_flat),
        "MAE": mean_absolute_error(
            nights_proof_df["cancelled"], nights_proof_df["expected"]
        ),
        "Empty": res_flat_rule["empty_rooms"],
        "Walks": res_flat_rule["walked_guests"],
        "Walks/1k": res_flat_rule["walks_per_1000"],
        "Cost (€)": res_flat_rule["cost_eur"],
        "Savings (€)": flat_cost - res_flat_rule["cost_eur"],
        "Ceiling": res_flat_rule["ceiling_met"],
    },
    {
        "Method": "Lookup Table",
        "Buffer": best_lookup_buffer,
        "AUC": roc_auc_score(proof["is_canceled"], prob_proof_lookup),
        "MAE": mean_absolute_error(
            nights_proof_lookup["cancelled"], nights_proof_lookup["expected"]
        ),
        "Empty": res_lookup_rule["empty_rooms"],
        "Walks": res_lookup_rule["walked_guests"],
        "Walks/1k": res_lookup_rule["walks_per_1000"],
        "Cost (€)": res_lookup_rule["cost_eur"],
        "Savings (€)": flat_cost - res_lookup_rule["cost_eur"],
        "Ceiling": res_lookup_rule["ceiling_met"],
    },
    {
        "Method": "Decision Tree",
        "Buffer": buf_dt,
        "AUC": roc_auc_score(proof["is_canceled"], prob_proof_dt),
        "MAE": mean_absolute_error(
            nights_proof_dt["cancelled"], nights_proof_dt["expected"]
        ),
        "Empty": res_dt["empty_rooms"],
        "Walks": res_dt["walked_guests"],
        "Walks/1k": res_dt["walks_per_1000"],
        "Cost (€)": res_dt["cost_eur"],
        "Savings (€)": flat_cost - res_dt["cost_eur"],
        "Ceiling": res_dt["ceiling_met"],
    },
    {
        "Method": "Random Forest",
        "Buffer": buf_rf,
        "AUC": roc_auc_score(proof["is_canceled"], prob_proof_rf),
        "MAE": mean_absolute_error(
            night_proof_rf["cancelled"], night_proof_rf["expected"]
        ),
        "Empty": res_rf["empty_rooms"],
        "Walks": res_rf["walked_guests"],
        "Walks/1k": res_rf["walks_per_1000"],
        "Cost (€)": res_rf["cost_eur"],
        "Savings (€)": flat_cost - res_rf["cost_eur"],
        "Ceiling": res_rf["ceiling_met"],
    },
    {
        "Method": "Logistic Regression",
        "Buffer": buf_lr,
        "AUC": roc_auc_score(proof["is_canceled"], prob_proof_lr),
        "MAE": mean_absolute_error(
            night_proof_lr["cancelled"], night_proof_lr["expected"]
        ),
        "Empty": res_lr["empty_rooms"],
        "Walks": res_lr["walked_guests"],
        "Walks/1k": res_lr["walks_per_1000"],
        "Cost (€)": res_lr["cost_eur"],
        "Savings (€)": flat_cost - res_lr["cost_eur"],
        "Ceiling": res_lr["ceiling_met"],
    },
]


print("\n" + "=" * 115)
print("METHOD COMPARISON ON THE PROOF PERIOD (2017-01-01 to 2017-08-31)")
print("=" * 115)
print(
    f"{'Method':<22} | {'Buf':>3} | {'AUC':>6} | {'MAE':>6} | "
    f"{'Empty':>6} | {'Walks':>5} | {'Walks/1k':>8} | {'Cost (€)':>14} | "
    f"{'Savings (€)':>14} | {'Ceiling':>7}"
)
print("-" * 115)
for row in models_data:
  print(
      f"{row['Method']:<22} | {row['Buffer']:>3} | {row['AUC']:>6.4f} |"
      f" {row['MAE']:>6.2f} | {row['Empty']:>6} | {row['Walks']:>5} |"
      f" {row['Walks/1k']:>8.2f} | €{row['Cost (€)']:>13,.2f} |"
      f" €{row['Savings (€)']:>13,.2f} | {str(row['Ceiling']):>7}"
  )
print("=" * 115 + "\n")
