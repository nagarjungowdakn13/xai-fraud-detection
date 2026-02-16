"""Train and evaluate baseline models on the synthetic_transactions dataset.

This script is used to generate *real* metrics for the paper's
Experimental Evaluation section (accuracy/SOTA, latency, and ablations)
on the synthetic test split.

Models:
  - Logistic Regression (baseline)
  - Random Forest
  - Gradient Boosting (XGBoost-style tree ensemble proxy)
  - Simple Ensemble (average of the three models' probabilities)

Features (from synthetic_transactions/*.csv):
  - amount (numeric)
  - hour-of-day (0-23)
  - day-of-week (0-6)
  - channel (web/mobile/pos; categorical)
  - region (categorical)

Outputs:
  - Prints per-model metrics (Acc, BalAcc, AUC, AUPRC, F1, latency) to stdout.
  - Writes a JSON summary to `synthetic_model_metrics.json` at repo root.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _make_features(
    df: pd.DataFrame,
    merchant_stats: pd.DataFrame | None = None,
    global_tx: float | None = None,
    global_rate: float | None = None,
) -> pd.DataFrame:
    """Derive a compact feature set from the synthetic transaction schema.

    In addition to basic temporal and amount features, we include simple
    merchant-level statistics computed from the training data only
    (transaction count and empirical fraud rate), passed in via
    ``merchant_stats``.
    """

    df_feat = df.copy()

    # Timestamp is ISO8601 string; extract hour and day-of-week
    dt = pd.to_datetime(df_feat["timestamp"], utc=True, errors="coerce")
    df_feat["hour"] = dt.dt.hour.fillna(0).astype(int)
    df_feat["dow"] = dt.dt.dayofweek.fillna(0).astype(int)

    # Attach merchant-level stats (computed from train only)
    if merchant_stats is not None:
        df_feat = df_feat.merge(merchant_stats, on="merchant_id", how="left")
        if global_tx is None:
            global_tx = float(df_feat["m_tx"].dropna().mean() or 0.0)
        if global_rate is None:
            global_rate = float(df_feat.get("label", 0).mean() or 0.0)
        df_feat["m_tx"].fillna(global_tx, inplace=True)
        df_feat["m_rate"].fillna(global_rate, inplace=True)
    else:
        # Fallback: no merchant stats available
        df_feat["m_tx"] = 0.0
        df_feat["m_rate"] = float(df_feat.get("label", 0).mean() or 0.0)

    features = pd.DataFrame(
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
    return features


def _build_pipeline(model) -> Pipeline:
    num_cols = ["amount", "hour", "dow", "merchant_tx", "merchant_rate"]
    cat_cols = ["channel", "region"]

    pre = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    return Pipeline([
        ("pre", pre),
        ("clf", model),
    ])


def _balanced_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    tpr = tp / (tp + fn + 1e-9)
    tnr = tn / (tn + fp + 1e-9)
    return float((tpr + tnr) / 2.0)


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    root = base / "data" / "raw" / "synthetic_transactions"
    train_path = root / "train.csv"
    test_path = root / "test.csv"
    if not train_path.exists() or not test_path.exists():
        raise SystemExit(f"Expected synthetic splits at {root} (train.csv/test.csv)")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    # Merchant-level stats from training data only
    m_group = train_df.groupby("merchant_id")["label"]
    m_stats = m_group.agg(["size", "sum"]).reset_index()
    m_stats.rename(columns={"size": "m_tx", "sum": "m_fraud"}, inplace=True)
    m_stats["m_rate"] = m_stats["m_fraud"] / m_stats["m_tx"].clip(lower=1)
    global_tx = float(m_stats["m_tx"].mean())
    global_rate = float(train_df["label"].mean())

    X_train = _make_features(
        train_df,
        merchant_stats=m_stats[["merchant_id", "m_tx", "m_rate"]],
        global_tx=global_tx,
        global_rate=global_rate,
    )
    y_train = train_df["label"].astype(int).to_numpy()
    X_test = _make_features(
        test_df,
        merchant_stats=m_stats[["merchant_id", "m_tx", "m_rate"]],
        global_tx=global_tx,
        global_rate=global_rate,
    )
    y_test = test_df["label"].astype(int).to_numpy()

    models = {
        "logreg": _build_pipeline(
            LogisticRegression(
                max_iter=1000,
                n_jobs=-1,
                class_weight="balanced",
            )
        ),
        "rf": _build_pipeline(
            RandomForestClassifier(
                n_estimators=200,
                n_jobs=-1,
                class_weight="balanced",
                random_state=42,
            )
        ),
        "gb": _build_pipeline(
            GradientBoostingClassifier(
                random_state=42,
            )
        ),
    }

    summary: dict[str, dict] = {}

    # Fit and evaluate individual models
    for name, pipe in models.items():
        print(f"=== Training {name} ===")
        pipe.fit(X_train, y_train)

        t0 = time.perf_counter()
        y_prob = pipe.predict_proba(X_test)[:, 1]
        infer_ms = (time.perf_counter() - t0) * 1000.0
        per_tx_ms = infer_ms / len(X_test)

        y_pred = (y_prob >= 0.5).astype(int)

        acc = accuracy_score(y_test, y_pred)
        bal_acc = _balanced_accuracy(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        auprc = average_precision_score(y_test, y_prob)
        f1 = f1_score(y_test, y_pred)

        metrics = {
            "accuracy": round(acc, 5),
            "balanced_accuracy": round(bal_acc, 5),
            "auc_roc": round(auc, 5),
            "auprc": round(auprc, 5),
            "f1": round(f1, 5),
            "latency_ms_total": round(infer_ms, 3),
            "latency_ms_per_tx": round(per_tx_ms, 5),
        }
        summary[name] = metrics
        print({"model": name, **metrics})

    # Ensemble: simple average of probabilities
    print("=== Evaluating ensemble (logreg + rf + gb) ===")
    probs = []
    for name in ("logreg", "rf", "gb"):
        pipe = models[name]
        t0 = time.perf_counter()
        y_prob = pipe.predict_proba(X_test)[:, 1]
        infer_ms = (time.perf_counter() - t0) * 1000.0
        probs.append(y_prob)
        summary.setdefault("ensemble_timing", {})[name] = round(infer_ms, 3)

    y_prob_ens = np.mean(probs, axis=0)
    y_pred_ens = (y_prob_ens >= 0.5).astype(int)

    acc = accuracy_score(y_test, y_pred_ens)
    bal_acc = _balanced_accuracy(y_test, y_pred_ens)
    auc = roc_auc_score(y_test, y_prob_ens)
    auprc = average_precision_score(y_test, y_prob_ens)
    f1 = f1_score(y_test, y_pred_ens)

    ens_metrics = {
        "accuracy": round(acc, 5),
        "balanced_accuracy": round(bal_acc, 5),
        "auc_roc": round(auc, 5),
        "auprc": round(auprc, 5),
        "f1": round(f1, 5),
        # Ensemble latency approximated as sum of constituent inference times
        "latency_ms_total": round(
            sum(summary["ensemble_timing"].values()), 3
        ),
    }
    summary["ensemble"] = ens_metrics
    print({"model": "ensemble", **ens_metrics})

    # Ablation: ensembles missing one component
    print("=== Ablation: ensembles missing one component ===")
    ablations: dict[str, dict] = {}
    configs = {
        "no_logreg": ("rf", "gb"),
        "no_rf": ("logreg", "gb"),
        "no_gb": ("logreg", "rf"),
    }
    for cfg_name, names in configs.items():
        cfg_probs = [models[n].predict_proba(X_test)[:, 1] for n in names]
        y_prob_cfg = np.mean(cfg_probs, axis=0)
        y_pred_cfg = (y_prob_cfg >= 0.5).astype(int)
        acc = accuracy_score(y_test, y_pred_cfg)
        bal_acc = _balanced_accuracy(y_test, y_pred_cfg)
        auc = roc_auc_score(y_test, y_prob_cfg)
        auprc = average_precision_score(y_test, y_prob_cfg)
        f1 = f1_score(y_test, y_pred_cfg)
        ablations[cfg_name] = {
            "accuracy": round(acc, 5),
            "balanced_accuracy": round(bal_acc, 5),
            "auc_roc": round(auc, 5),
            "auprc": round(auprc, 5),
            "f1": round(f1, 5),
        }
        print({"config": cfg_name, **ablations[cfg_name]})

    summary["ablations"] = ablations

    out_path = base / "synthetic_model_metrics.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote metrics summary to {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
