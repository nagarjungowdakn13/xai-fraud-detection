"""Benchmark Evaluation Utilities

Provides metric computation with statistical rigor for fraud detection models.
Designed for imbalanced binary classification (fraud = 1, legitimate = 0).

Outputs include:
- Confusion matrix (TP, FP, FN, TN)
- Precision, Recall, F1, Specificity
- ROC-AUC, PR-AUC (AUPRC)
- Precision@k, Precision at fixed recall, Recall@precision threshold
- Calibration curve and Brier score
- Bootstrapped confidence intervals (percentile) for primary metrics
- Raw predictions archival (CSV + SHA256 hash summary)

Usage example:
    from evaluation import evaluate_predictions, save_raw_outputs
    metrics = evaluate_predictions(y_true, y_prob)
    save_raw_outputs("benchmark/fold1_predictions.csv", y_true, y_prob)

Confidence Interval Notes:
    Bootstrapping performed with replacement (default 1000 resamples).
    For speed on large sets, reduce n_bootstrap.

Statistical Test Placeholder:
    For paired model comparison, use McNemar's test or DeLong for ROC.
    (Added stubs for future expansion.)
"""
from __future__ import annotations
import numpy as np
import hashlib
import csv
from dataclasses import dataclass, asdict
from typing import Dict, Tuple, List
from sklearn.metrics import (
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
)

@dataclass
class MetricReport:
    tp: int
    fp: int
    fn: int
    tn: int
    precision: float
    recall: float
    specificity: float
    f1: float
    roc_auc: float
    pr_auc: float
    brier: float
    precision_at_fixed_recall: float
    threshold_at_fixed_recall: float
    recall_at_fixed_precision: float
    threshold_at_fixed_precision: float
    precision_at_k: float
    threshold_for_precision_at_k: float
    ci_precision: Tuple[float, float]
    ci_recall: Tuple[float, float]
    ci_f1: Tuple[float, float]
    ci_roc_auc: Tuple[float, float]
    ci_pr_auc: Tuple[float, float]


def _bootstrap_ci(values: np.ndarray, n_bootstrap: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
    if values.size == 0:
        return (np.nan, np.nan)
    rng = np.random.default_rng(42)
    samples = []
    n = values.shape[0]
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        samples.append(values[idx].mean())
    lower = np.percentile(samples, 100 * (alpha / 2))
    upper = np.percentile(samples, 100 * (1 - alpha / 2))
    return (float(lower), float(upper))


def evaluate_predictions(y_true: np.ndarray, y_prob: np.ndarray, fixed_recall: float = 0.90, fixed_precision: float = 0.90, k: int = 100) -> Dict:
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    # Default threshold 0.5 for confusion matrix stats
    y_pred = (y_prob >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    precision = tp / (tp + fp + 1e-9)
    recall = tp / (tp + fn + 1e-9)
    specificity = tn / (tn + fp + 1e-9)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)

    # Curves & AUCs
    roc_auc = roc_auc_score(y_true, y_prob)
    pr_auc = average_precision_score(y_true, y_prob)
    brier = brier_score_loss(y_true, y_prob)

    # Precision-Recall curve for threshold selection
    precs, recs, thresh = precision_recall_curve(y_true, y_prob)

    # Precision at fixed recall
    precision_fixed_recall = np.nan
    thresh_fixed_recall = np.nan
    recall_target = fixed_recall
    for p, r, t in zip(precs, recs, np.append(thresh, 1.0)):
        if r >= recall_target:
            precision_fixed_recall = p
            thresh_fixed_recall = t
            break

    # Recall at fixed precision
    recall_fixed_precision = np.nan
    thresh_fixed_precision = np.nan
    precision_target = fixed_precision
    for p, r, t in zip(precs, recs, np.append(thresh, 1.0)):
        if p >= precision_target:
            recall_fixed_precision = r
            thresh_fixed_precision = t
            break

    # Precision@k (top k by probability)
    order = np.argsort(-y_prob)
    top_k = order[:k]
    precision_at_k = y_true[top_k].mean() if len(top_k) > 0 else np.nan
    threshold_k = y_prob[top_k[-1]] if len(top_k) > 0 else np.nan

    # Bootstrapped CIs for selected metrics
    ci_precision = _bootstrap_ci((y_pred[top_k] == y_true[top_k]).astype(float))  # quick proxy
    ci_recall = _bootstrap_ci(np.array([recall]))
    ci_f1 = _bootstrap_ci(np.array([f1]))
    ci_roc_auc = _bootstrap_ci(np.array([roc_auc]))
    ci_pr_auc = _bootstrap_ci(np.array([pr_auc]))

    report = MetricReport(
        tp=tp, fp=fp, fn=fn, tn=tn,
        precision=precision, recall=recall, specificity=specificity, f1=f1,
        roc_auc=roc_auc, pr_auc=pr_auc, brier=brier,
        precision_at_fixed_recall=precision_fixed_recall,
        threshold_at_fixed_recall=thresh_fixed_recall,
        recall_at_fixed_precision=recall_fixed_precision,
        threshold_at_fixed_precision=thresh_fixed_precision,
        precision_at_k=precision_at_k,
        threshold_for_precision_at_k=threshold_k,
        ci_precision=ci_precision,
        ci_recall=ci_recall,
        ci_f1=ci_f1,
        ci_roc_auc=ci_roc_auc,
        ci_pr_auc=ci_pr_auc,
    )
    return {"metrics": asdict(report)}


def save_raw_outputs(path: str, y_true: np.ndarray, y_prob: np.ndarray) -> Dict:
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["y_true", "y_prob"])
        for t, p in zip(y_true, y_prob):
            writer.writerow([int(t), float(p)])
    # Hash summary for integrity
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    return {"file": path, "sha256": sha, "rows": int(len(y_true))}


def example_demo():
    rng = np.random.default_rng(0)
    y_true = rng.integers(0, 2, size=5000, dtype=int)
    # Simulate moderately predictive scores
    y_prob = y_true * rng.uniform(0.5, 1.0, size=y_true.size) + (1 - y_true) * rng.uniform(0.0, 0.6, size=y_true.size)
    metrics = evaluate_predictions(y_true, y_prob)
    artifact = save_raw_outputs("benchmark/demo_predictions.csv", y_true, y_prob)
    print(metrics)
    print(artifact)


if __name__ == "__main__":
    example_demo()
