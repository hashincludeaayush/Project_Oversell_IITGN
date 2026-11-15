"""Buffer search and night scoring logic using the client evaluation contract."""

import numpy as np
import pandas as pd
from contract import nightly_table, night_cost


class NoCompliantBufferError(ValueError):
    """Raised when no searched buffer satisfies the client's walk ceiling."""


def evaluate_buffer(
    nights_df: pd.DataFrame,
    buffer: int,
) -> dict:
    """Score a specific whole-room buffer against nightly aggregated cancellations."""
    k = np.maximum(0, np.round(nights_df["expected"] - buffer))
    res = night_cost(nights_df, k)
    res["buffer"] = buffer
    return res


def find_optimal_buffer(
    nights_df: pd.DataFrame,
    min_buffer: int = 0,
    max_buffer: int = 30,
) -> tuple[int, dict]:
    """Find the cheapest integer buffer on Choose that meets the walk ceiling (<= 10 / 1000)."""
    valid_candidates = []

    for b in range(min_buffer, max_buffer + 1):
        res = evaluate_buffer(nights_df, b)
        if res["ceiling_met"]:
            valid_candidates.append(res)

    if valid_candidates:
        # Pick the lowest cost buffer among those meeting the ceiling
        best = min(valid_candidates, key=lambda x: x["cost_eur"])
        return best["buffer"], best
    raise NoCompliantBufferError(
        f"No buffer from {min_buffer} to {max_buffer} meets the walk ceiling."
    )
