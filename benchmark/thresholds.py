"""Cost-sensitive threshold optimization.
Usage: python benchmark/thresholds.py predictions.csv --c_fp 1.0 --c_fn 5.0
CSV must include y_true,y_prob
"""
import argparse
import numpy as np
import pandas as pd


def expected_cost(y_true: np.ndarray, y_prob: np.ndarray, threshold: float, c_fp: float, c_fn: float) -> float:
    y_pred = (y_prob >= threshold).astype(int)
    fp = ((y_pred == 1) & (y_true == 0)).sum()
    fn = ((y_pred == 0) & (y_true == 1)).sum()
    return c_fp * fp + c_fn * fn


def sweep_thresholds(y_true, y_prob, c_fp, c_fn, steps=201):
    best_t, best_cost = None, float('inf')
    for t in np.linspace(0,1,steps):
        cost = expected_cost(y_true, y_prob, t, c_fp, c_fn)
        if cost < best_cost:
            best_t, best_cost = float(t), float(cost)
    return best_t, best_cost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv')
    ap.add_argument('--c_fp', type=float, default=1.0)
    ap.add_argument('--c_fn', type=float, default=5.0)
    args = ap.parse_args()
    df = pd.read_csv(args.csv)
    if not {'y_true','y_prob'}.issubset(df.columns):
        raise ValueError('CSV must contain y_true,y_prob')
    y_true = df['y_true'].values.astype(int)
    y_prob = df['y_prob'].values.astype(float)
    t, cost = sweep_thresholds(y_true, y_prob, args.c_fp, args.c_fn)
    print(f'Best threshold: {t:.4f}, Expected cost: {cost:.2f} (C_FP={args.c_fp}, C_FN={args.c_fn})')

if __name__ == '__main__':
    main()
