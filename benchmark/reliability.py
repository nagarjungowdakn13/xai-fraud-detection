"""Reliability diagram & Expected Calibration Error computation.
Usage: python benchmark/reliability.py path/to/predictions.csv
CSV expected columns: y_true, y_prob
"""
import sys
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, bins: int = 10) -> Tuple[float, dict]:
    bin_edges = np.linspace(0.0, 1.0, bins + 1)
    indices = np.digitize(y_prob, bin_edges, right=True) - 1
    ece = 0.0
    bin_stats = {}
    for b in range(bins):
        mask = indices == b
        if not np.any(mask):
            continue
        conf = y_prob[mask].mean()
        acc = y_true[mask].mean()
        weight = mask.sum() / len(y_true)
        ece += weight * abs(acc - conf)
        bin_stats[b] = {"count": int(mask.sum()), "accuracy": float(acc), "confidence": float(conf)}
    return ece, bin_stats


def plot_reliability(bin_stats: dict, bins: int, out_file: str):
    xs = []
    ys = []
    for b in range(bins):
        stats = bin_stats.get(b)
        if not stats:
            continue
        xs.append(stats["confidence"])
        ys.append(stats["accuracy"])
    plt.figure(figsize=(5,5))
    plt.plot([0,1],[0,1], 'k--', label='Perfect')
    plt.scatter(xs, ys, color='blue')
    plt.xlabel('Mean Confidence')
    plt.ylabel('Empirical Accuracy')
    plt.title('Reliability Diagram')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_file)
    print(f"Saved {out_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python benchmark/reliability.py predictions.csv")
        return
    path = sys.argv[1]
    df = pd.read_csv(path)
    if not {'y_true','y_prob'}.issubset(df.columns):
        raise ValueError("CSV must contain y_true,y_prob columns")
    y_true = df['y_true'].values.astype(int)
    y_prob = df['y_prob'].values.astype(float)
    ece, stats = expected_calibration_error(y_true, y_prob, bins=15)
    print(f"ECE: {ece:.4f}")
    plot_reliability(stats, bins=15, out_file='reliability.png')

if __name__ == '__main__':
    main()
