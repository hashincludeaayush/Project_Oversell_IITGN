"""Machine learning model pipelines for cancellation probability estimation."""

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

# 1. Group the features approved by your Data Lead into Numbers vs Categories
NUMERICAL_FEATURES = [
    "lead_time", "arrival_date_week_number", "arrival_date_day_of_month",
    "stays_in_weekend_nights", "stays_in_week_nights", "adults", "children",
    "babies", "is_repeated_guest", "previous_cancellations",
    "previous_bookings_not_canceled",
]

CATEGORICAL_FEATURES = [
    "hotel", "arrival_date_month", "meal", "country", "market_segment",
    "distribution_channel", "reserved_room_type", "deposit_type", "agent",
    "company", "customer_type",
]

FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
# print(len(FEATURE_COLUMNS), len(NUMERICAL_FEATURES), len(CATEGORICAL_FEATURES))

def get_preprocessor(scale_numeric: bool = True) -> ColumnTransformer:
    """Build column transformer for scaling numbers and one-hot encoding categories."""
    num_step = StandardScaler() if scale_numeric else "passthrough"
    return ColumnTransformer(
        transformers=[
            ("num", num_step, NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def build_logistic_regression() -> Pipeline:
    """Logistic Regression pipeline with standardized numerics and one-hot categories."""
    return Pipeline([
        ("prep", get_preprocessor(scale_numeric=True)),
        ("clf", LogisticRegression(max_iter=500, random_state=42)),
    ])


def build_decision_tree(max_depth: int = 10, min_samples_leaf: int = 50) -> Pipeline:
    """Decision Tree pipeline with tree depth limits to prevent overfitting."""
    return Pipeline([
        ("prep", get_preprocessor(scale_numeric=False)),
        ("clf", DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=42
        )),
    ])


def build_random_forest(n_estimators: int = 100, max_depth: int = 12) -> Pipeline:
    """Random Forest pipeline with 100 trees."""
    return Pipeline([
        ("prep", get_preprocessor(scale_numeric=False)),
        ("clf", RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=20,
            n_jobs=-1,
            random_state=42
        )),
    ])