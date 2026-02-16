"""Train a simple baseline on dataset train split and score test split.
Outputs predictions CSV with y_true, y_prob and group columns (region, merchant_id, channel).

Usage:
  python scripts/score_baseline_on_dataset.py --name synthetic_transactions --out ensemble_outputs/predictions_baseline.csv
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

REQUIRED = ['timestamp','account_id','counterparty_id','device_id','ip_address','merchant_id','amount','currency','channel','label']


def load_splits(base: Path, name: str):
    base_raw = base / 'data' / 'raw' / name
    train = pd.read_csv(base_raw / 'train.csv')
    test = pd.read_csv(base_raw / 'test.csv')
    return train, test


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Derive hour and weekend
    ts = pd.to_datetime(df['timestamp'], errors='coerce')
    df['hour'] = ts.dt.hour.fillna(0).astype(int)
    df['is_weekend'] = ts.dt.dayofweek.isin([5,6]).astype(int)
    df['log_amount'] = np.log1p(df['amount'].astype(float))
    # Keep helpful group columns if present
    for col in ['region','merchant_id','channel']:
        if col not in df.columns:
            df[col] = 'UNK'
    return df


def train_and_score(train: pd.DataFrame, test: pd.DataFrame):
    train = build_features(train)
    test = build_features(test)
    y_train = train['label'].astype(int).values
    y_test = test['label'].astype(int).values

    num_cols = ['log_amount', 'hour', 'is_weekend']
    cat_cols = ['channel']  # keep it small; large-cardinality merchant is not encoded here

    pre = ColumnTransformer([
        ('num','passthrough', num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
    ])

    clf = Pipeline([
        ('prep', pre),
        ('lr', LogisticRegression(max_iter=300))
    ])

    clf.fit(train, y_train)
    y_prob = clf.predict_proba(test)[:,1]
    auc = roc_auc_score(y_test, y_prob)

    out = test[['label','merchant_id','region','channel']].copy()
    out.rename(columns={'label':'y_true'}, inplace=True)
    out['y_prob'] = y_prob
    return out, auc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--out', default='ensemble_outputs/predictions_baseline.csv')
    args = ap.parse_args()

    base = Path(__file__).resolve().parents[1]
    out_dir = base / 'ensemble_outputs'
    out_dir.mkdir(exist_ok=True)

    train, test = load_splits(base, args.name)
    preds, auc = train_and_score(train, test)
    preds.to_csv(out_dir / Path(args.out).name, index=False)
    print(f"Wrote predictions to {out_dir / Path(args.out).name} (AUC={auc:.4f})")

if __name__ == '__main__':
    main()
