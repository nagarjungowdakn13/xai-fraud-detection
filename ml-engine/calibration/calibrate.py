"""Calibration utilities: isotonic and Platt scaling (logistic).
Usage:
  python ml-engine/calibration/calibrate.py --preds predictions.csv --method isotonic --out calibrated.csv
CSV requires columns: y_true, y_prob (optional y_logit for Platt with logits)
"""
import argparse
import pandas as pd
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def isotonic_calibrate(y_true, y_prob):
    iso = IsotonicRegression(out_of_bounds='clip')
    iso.fit(y_prob, y_true)
    return iso.predict(y_prob)


def platt_calibrate(y_true, y_prob):
    # Logistic regression on scores as a single feature
    X = y_prob.reshape(-1, 1)
    lr = LogisticRegression(max_iter=200)
    lr.fit(X, y_true)
    return lr.predict_proba(X)[:,1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preds', required=True)
    ap.add_argument('--method', choices=['isotonic','platt'], default='isotonic')
    ap.add_argument('--out', default='calibrated.csv')
    args = ap.parse_args()

    df = pd.read_csv(args.preds)
    if not {'y_true','y_prob'}.issubset(df.columns):
        raise ValueError('predictions.csv must contain y_true,y_prob')
    y_true = df['y_true'].values.astype(int)
    y_prob = df['y_prob'].values.astype(float)

    if args.method == 'isotonic':
        y_cal = isotonic_calibrate(y_true, y_prob)
    else:
        y_cal = platt_calibrate(y_true, y_prob)

    out = df.copy()
    out['y_prob_cal'] = y_cal
    out.to_csv(args.out, index=False)
    print(f"Wrote calibrated predictions to {args.out}")

if __name__ == '__main__':
    main()
