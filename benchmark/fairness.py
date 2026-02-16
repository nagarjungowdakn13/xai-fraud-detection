"""Fairness metrics across groups.
Computes demographic parity difference and equal opportunity difference per group attribute.
Usage: python benchmark/fairness.py predictions.csv --group merchant_id
CSV must include: y_true, y_prob, and group column(s)
"""
import argparse
import pandas as pd
import numpy as np


def binarize(y_prob, threshold: float):
    return (y_prob >= threshold).astype(int)


def demographic_parity(df: pd.DataFrame, group_col: str, threshold: float):
    df = df.copy()
    df['y_pred'] = binarize(df['y_prob'].values, threshold)
    rates = df.groupby(group_col)['y_pred'].mean()
    return rates.max() - rates.min(), rates.to_dict()


def equal_opportunity(df: pd.DataFrame, group_col: str, threshold: float):
    df = df.copy()
    df['y_pred'] = binarize(df['y_prob'].values, threshold)
    tpr = df[df['y_true']==1].groupby(group_col)['y_pred'].mean()
    # handle groups without positives
    tpr = tpr.fillna(0.0)
    return tpr.max() - tpr.min(), tpr.to_dict()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv', type=str)
    ap.add_argument('--group', required=True)
    ap.add_argument('--threshold', type=float, default=0.5)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    for col in ['y_true','y_prob', args.group]:
        if col not in df.columns:
            raise ValueError(f'Missing column: {col}')
    dp_diff, dp_rates = demographic_parity(df, args.group, args.threshold)
    eo_diff, eo_rates = equal_opportunity(df, args.group, args.threshold)

    print(f'Demographic Parity Diff: {dp_diff:.4f}')
    print(f'Rates: {dp_rates}')
    print(f'Equal Opportunity Diff: {eo_diff:.4f}')
    print(f'TPR by group: {eo_rates}')

if __name__ == '__main__':
    main()
