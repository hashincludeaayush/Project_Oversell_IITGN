
import contract
import data
import features
from models.helpers import run_on_choose, METHODS, run_on_proof, build_comparison_table

raw = data.read_raw()
prepared_df = features.prepare_bookings(raw)
train, choose, proof = contract.split_periods(prepared_df)


choose_results = []
proof_results = []


for name, factory in METHODS.items():
  # Fit on train, tune buffer on choose
  cand = run_on_choose(name, factory, train, choose)
  choose_results.append(cand)
  # Evaluate on proof with frozen buffer
  proof_eval = run_on_proof(cand, proof)
  proof_results.append(proof_eval)

# Build Tables
choose_table = build_comparison_table(choose_results, choose)
proof_table = build_comparison_table(proof_results, proof)

# Select Winner on Choose (by highest AUC among compliant methods)
eligible_methods = choose_table[choose_table["Ceiling met"]]
winner_row = eligible_methods.loc[eligible_methods["AUC"].idxmax()]
winner_name = winner_row["Method"]
winner_cand = next(c for c in choose_results if c["method"] == winner_name)
print("\n" + "=" * 105)
print(
    "TABLE 1: CHOOSE PERIOD TUNING & METHOD SELECTION (2016-07-01 to 2016-12-31)"
)
print("=" * 105)
print(choose_table.to_string(index=False))
print("=" * 105 + "\n")
print(
    f">>> Selected on choose: {winner_name} "
    f"(Buffer={winner_cand['buffer']}, "
    f"Cost=€{winner_row['Cost (€)']:,.2f}, "
    f"AUC={winner_row['AUC']:.4f})\n"
)
print("=" * 105)
print("TABLE 2: FINAL PROOF PERIOD DELIVERABLE (2017-01-01 to 2017-08-31)")
print("=" * 105)
print(proof_table.to_string(index=False))
print("=" * 105 + "\n")