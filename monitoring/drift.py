"""Drift monitoring utilities.
Provides PSI, KS-test, rolling AUC tracking placeholders.
Usage examples:
python monitoring/drift.py reference.csv current.csv
CSV columns expected: feature_*, y_true (optional), y_prob (optional)
"""
import sys
import numpy as np
import pandas as pd
from typing import List, Tuple
from scipy.stats import ks_2samp


def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    cut_points = np.linspace(0, 1, bins + 1)
    def bin_fracs(values):
        # Normalize to [0,1] range for numeric features
        v = values.astype(float)
        if v.max() > v.min():
            v = (v - v.min()) / (v.max() - v.min())
        counts = np.histogram(v, bins=cut_points)[0].astype(float)
        fracs = counts / counts.sum() if counts.sum() else np.zeros_like(counts)
        return fracs
    e_fracs = bin_fracs(expected)
    a_fracs = bin_fracs(actual)
    total = 0.0
    for e, a in zip(e_fracs, a_fracs):
        if e == 0 or a == 0:
            continue
        total += (a - e) * np.log(a / e)
    return total


def ks_stat(expected: np.ndarray, actual: np.ndarray) -> float:
    stat, _ = ks_2samp(expected, actual)
    return stat


def analyze(reference: pd.DataFrame, current: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    rows = []
    for col in feature_cols:
        if col not in reference.columns or col not in current.columns:
            continue
        e = reference[col].values
        a = current[col].values
        rows.append({
            'feature': col,
            'psi': psi(e, a),
            'ks': ks_stat(e, a)
        })
    return pd.DataFrame(rows)


def main():
    if len(sys.argv) < 3:
        print("Usage: python monitoring/drift.py reference.csv current.csv")
        return
    ref = pd.read_csv(sys.argv[1])
    cur = pd.read_csv(sys.argv[2])
    feature_cols = [c for c in ref.columns if c.startswith('feature_')]
    report = analyze(ref, cur, feature_cols)
    print(report.sort_values('psi', ascending=False).to_string(index=False))

if __name__ == '__main__':
    main()
