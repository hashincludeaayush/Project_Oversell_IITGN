"""Choose and freeze a policy before scoring the final Proof period."""

from pathlib import Path

import contract
import data
import features
from models.buffer import NoCompliantBufferError
from models.helpers import (
    METHODS,
    build_comparison_table,
    run_on_choose,
    run_on_proof,
    score_flat_rule_reference,
    select_winner,
)
from models.persistence import load_selected_policy, save_selected_policy

DEFAULT_POLICY_PATH = (
    Path(__file__).resolve().parent.parent / "models" / "selected_policy.joblib"
)


def choose_and_freeze(
    train,
    choose,
    *,
    methods=METHODS,
    policy_path=DEFAULT_POLICY_PATH,
):
    """Fit on Train, select on Choose, and persist/reload the frozen winner."""
    choose_results = []
    discarded = {}

    for name, factory in methods.items():
        try:
            choose_results.append(run_on_choose(name, factory, train, choose))
        except NoCompliantBufferError as exc:
            discarded[name] = str(exc)

    if not choose_results:
        raise ValueError("No candidate policy meets the walk ceiling on Choose.")

    flat_candidate = next(
        (
            candidate
            for candidate in choose_results
            if candidate["method"] == "Client Flat Rule"
        ),
        None,
    )
    # The contract requires the flat-rule safety margin to be Choose-selected under the same ceiling.
    if flat_candidate is None:
        raise ValueError("The Choose comparison requires a compliant Client Flat Rule baseline.")

    choose_table = build_comparison_table(choose_results, choose)
    winner, winner_row = select_winner(choose_results, choose_table)
    saved_path = save_selected_policy(winner, winner_row, policy_path)
    frozen_policy = load_selected_policy(saved_path)

    return {
        "choose_results": choose_results,
        "choose_table": choose_table,
        "winner_row": winner_row,
        "winner": winner,
        "frozen_policy": frozen_policy,
        "flat_candidate": flat_candidate,
        "discarded": discarded,
        "policy_path": saved_path,
    }


def evaluate_frozen_policy(selection, proof):
    """Score only the persisted winner, plus the required flat-rule reference."""
    frozen_policy = selection["frozen_policy"]
    winner_proof = run_on_proof(frozen_policy, proof)

    if frozen_policy["method"] == "Client Flat Rule":
        flat_cost = winner_proof["metrics"]["cost_eur"]
    else:
        flat_reference = score_flat_rule_reference(selection["flat_candidate"], proof)
        flat_cost = flat_reference["metrics"]["cost_eur"]

    proof_table = build_comparison_table(
        [winner_proof],
        proof,
        flat_cost=flat_cost,
    )
    return winner_proof, proof_table


def main():
    raw = data.read_raw()
    prepared = features.prepare_bookings(raw)
    train, choose, proof = contract.split_periods(prepared)

    selection = choose_and_freeze(train, choose)
    print("CHOOSE PERIOD MODEL SELECTION (2016-07-01 to 2016-12-31)")
    print(selection["choose_table"].to_string(index=False))
    for name, reason in selection["discarded"].items():
        print(f"Discarded {name}: {reason}")
    print(
        f"Selected and frozen on Choose: {selection['frozen_policy']['method']} "
        f"(buffer={selection['frozen_policy']['buffer']}, "
        f"AUC={selection['winner_row']['AUC']:.4f}; "
        f"saved to {selection['policy_path']})"
    )

    _, proof_table = evaluate_frozen_policy(selection, proof)
    print("FINAL PROOF PERIOD EVALUATION (2017-01-01 to 2017-08-31)")
    print(proof_table.to_string(index=False))


if __name__ == "__main__":
    main()
