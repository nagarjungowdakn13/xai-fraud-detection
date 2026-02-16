"""Compute threshold–metric–value curves for the synthetic dataset.

This script trains a Logistic Regression baseline on the synthetic
train split, evaluates on the validation split, and scans a grid of
thresholds to compute precision, recall, F1, accuracy, and expected
value under the paper's cost model.

Outputs:
  - synthetic_threshold_curve.csv at the repo root with columns:
    threshold, precision, recall, f1, accuracy,
    expected_value, expected_value_norm.
  - Prints the threshold that maximises expected value.

The feature construction and splitting follow scripts/eval_synthetic_models.py
so that numbers are consistent with the Experimental Evaluation section.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _make_features(
    df: pd.DataFrame,
    merchant_stats: pd.DataFrame,
    global_tx: float,
    global_rate: float,
) -> pd.DataFrame:
    """Replicate the compact feature set used in eval_synthetic_models.

    Features:
      - amount (numeric)
      - hour-of-day (0-23)
      - day-of-week (0-6)
      - merchant_tx (transaction count from train only)
      - merchant_rate (empirical fraud rate from train only)
      - channel (categorical)
      - region (categorical, default "UNK" if missing)
    """
    df_feat = df.copy()

    dt = pd.to_datetime(df_feat["timestamp"], utc=True, errors="coerce")
    df_feat["hour"] = dt.dt.hour.fillna(0).astype(int)
    df_feat["dow"] = dt.dt.dayofweek.fillna(0).astype(int)

    df_feat = df_feat.merge(merchant_stats, on="merchant_id", how="left")
    df_feat["m_tx"].fillna(global_tx, inplace=True)
    df_feat["m_rate"].fillna(global_rate, inplace=True)

    return pd.DataFrame(
        {
            "amount": df_feat["amount"].astype(float),
            "hour": df_feat["hour"].astype(int),
            "dow": df_feat["dow"].astype(int),
            "merchant_tx": df_feat["m_tx"].astype(float),
            "merchant_rate": df_feat["m_rate"].astype(float),
            "channel": df_feat["channel"].astype(str),
            "region": df_feat.get("region", "UNK").astype(str),
        }
    )


def _build_logreg_pipeline() -> Pipeline:
    num_cols = ["amount", "hour", "dow", "merchant_tx", "merchant_rate"]
    cat_cols = ["channel", "region"]

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    clf = LogisticRegression(
        max_iter=1000,
        n_jobs=-1,
        class_weight="balanced",
    )
    return Pipeline([("pre", pre), ("clf", clf)])


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    root = base / "data" / "raw" / "synthetic_transactions"

    train_path = root / "train.csv"
    valid_path = root / "valid.csv"
    if not train_path.exists() or not valid_path.exists():
        raise SystemExit(
            f"Expected synthetic splits at {root} (train.csv/valid.csv)"
        )

    train_df = pd.read_csv(train_path)
    valid_df = pd.read_csv(valid_path)

    # Merchant-level stats from training data only
    m_group = train_df.groupby("merchant_id")["label"]
    m_stats = m_group.agg(["size", "sum"]).reset_index()
    m_stats.rename(columns={"size": "m_tx", "sum": "m_fraud"}, inplace=True)
    m_stats["m_rate"] = m_stats["m_fraud"] / m_stats["m_tx"].clip(lower=1)
    global_tx = float(m_stats["m_tx"].mean())
    global_rate = float(train_df["label"].mean())
    merchant_stats = m_stats[["merchant_id", "m_tx", "m_rate"]]

    X_train = _make_features(train_df, merchant_stats, global_tx, global_rate)
    y_train = train_df["label"].astype(int).to_numpy()
    X_valid = _make_features(valid_df, merchant_stats, global_tx, global_rate)
    y_valid = valid_df["label"].astype(int).to_numpy()

    pipe = _build_logreg_pipeline()
    pipe.fit(X_train, y_train)

    y_prob = pipe.predict_proba(X_valid)[:, 1]

    thresholds = np.linspace(0.0, 1.0, 101)
    rows = []
    ev_values = []

    for tau in thresholds:
        y_pred = (y_prob >= tau).astype(int)
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_valid, y_pred, average="binary", zero_division=0
        )
        acc = accuracy_score(y_valid, y_pred)

        tp = int(((y_valid == 1) & (y_pred == 1)).sum())
        fp = int(((y_valid == 0) & (y_pred == 1)).sum())
        fn = int(((y_valid == 1) & (y_pred == 0)).sum())

        # Cost model from the paper
        ev = 50 * tp - 10 * fp - 500 * fn

        rows.append(
            {
                "threshold": float(tau),
                "precision": float(prec),
                "recall": float(rec),
                "f1": float(f1),
                "accuracy": float(acc),
                "expected_value": float(ev),
            }
        )
        ev_values.append(ev)

    ev_array = np.array(ev_values, dtype=float)
    # Normalise expected value to [0, 1] for plotting, preserving shape
    # even when all values are negative.
    if ev_array.size == 0:
        ev_norm = np.zeros(0, dtype=float)
    else:
        ev_min = ev_array.min()
        ev_max = ev_array.max()
        if ev_max - ev_min <= 0:
            ev_norm = np.zeros_like(ev_array, dtype=float)
        else:
            ev_norm = (ev_array - ev_min) / (ev_max - ev_min)

    for row, norm in zip(rows, ev_norm):
        row["expected_value_norm"] = float(norm)

    # Find optimal threshold according to expected value
    best_idx = int(ev_array.argmax()) if ev_array.size else 0
    best_tau = float(thresholds[best_idx])
    best_ev = float(ev_array[best_idx]) if ev_array.size else 0.0

    out_path = base / "synthetic_threshold_curve.csv"
    pd.DataFrame(rows).to_csv(out_path, index=False)

    print(f"Wrote threshold curve to {out_path}")
    print(f"Best threshold tau* = {best_tau:.4f} with expected value {best_ev:.2f}")


if __name__ == "__main__":  # pragma: no cover
    main()
