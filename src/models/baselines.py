"""Baseline cancellation predictors: Flat Rule and Lookup Table.

These provide the benchmarks that any machine learning model must beat.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


class FlatRuleModel:
    """The client's current baseline rule.

    Assigns each booking a cancellation probability equal to the historical
    cancellation rate of its hotel during the training period.
    """

    def __init__(self) -> None:
        self.hotel_rates: dict[str, float] = {}
        self.overall_rate: float|None = None
        # 37.04

    def fit(self, train_df: pd.DataFrame) -> "FlatRuleModel":
        """Compute historical cancellation rate per hotel from training data."""
        self.overall_rate = float(train_df["is_canceled"].mean())
        self.hotel_rates = (
            train_df.groupby("hotel")["is_canceled"].mean().to_dict()
        )
        return self

    def predict_probability(self, df: pd.DataFrame) -> np.ndarray:
        """Return cancellation probability for each booking."""
        if self.overall_rate is None:
            raise ValueError("Model is not fitted yet. Call fit(train_df) first.")
        return df["hotel"].map(self.hotel_rates).fillna(self.overall_rate).to_numpy(dtype=float)



class LookupTableModel:
    """A segment-based lookup table.

    Assigns each booking a probability based on (hotel, market_segment, lead_time_bin).
    If a combination was not seen in training, it falls back to the hotel rate,
    and then to the overall rate.
    """

    def __init__(self) -> None:
        self.lookup_rates: dict[tuple, float] = {}
        self.hotel_rates: dict[str, float] = {}
        self.overall_rate: float | None = None

    @staticmethod
    def _bin_lead_time(lead_times: pd.Series) -> pd.Series:
        """Bin lead time into 5 operational windows."""
        bins = [-1, 7, 30, 90, 180, 1000]
        labels = ["0-7d", "8-30d", "31-90d", "91-180d", "180d+"]
        return pd.cut(lead_times, bins=bins, labels=labels).astype(str)

    def fit(self, train_df: pd.DataFrame) -> "LookupTableModel":
        """Compute average cancellation rate by hotel, market segment, and lead time bin."""
        self.overall_rate = float(train_df["is_canceled"].mean())
        self.hotel_rates = train_df.groupby("hotel")["is_canceled"].mean().to_dict()

        df = train_df.copy()
        df["lead_bin"] = self._bin_lead_time(df["lead_time"])

        # Compute mean cancellation rate for each group
        grouped = df.groupby(["hotel", "market_segment", "lead_bin"])["is_canceled"].mean()
        self.lookup_rates = grouped.to_dict()
        return self

    def predict_probability(self, df: pd.DataFrame) -> np.ndarray:
        """Return looked-up cancellation probability for each booking."""
        if self.overall_rate is None:
            raise ValueError("Model is not fitted yet. Call fit(train_df) first.")

        df_copy = df.copy()
        df_copy["lead_bin"] = self._bin_lead_time(df_copy["lead_time"])

        keys = list(zip(df_copy["hotel"], df_copy["market_segment"], df_copy["lead_bin"]))
        probs = []
        for key in keys:
            if key in self.lookup_rates:
                probs.append(self.lookup_rates[key])
            elif key[0] in self.hotel_rates:
                probs.append(self.hotel_rates[key[0]])
            else:
                probs.append(self.overall_rate)

        return np.array(probs, dtype=float)