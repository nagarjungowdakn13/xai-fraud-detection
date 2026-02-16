"""Feature Engineering Pipeline

Generates transaction-level and aggregated features, including temporal and graph-derived placeholders.

Usage:
    python feature_engineering/feature_pipeline.py --input data/banking_transactions.csv --output data/features.csv
"""
import argparse
import csv
import math
from datetime import datetime
from collections import defaultdict

FEATURE_COLUMNS = [
    'transaction_id','user_id','merchant_id','device_id','timestamp','amount','label',
    # Engineered features
    'hour','is_weekend','log_amount','user_tx_count','merchant_tx_count','avg_user_amount','avg_merchant_amount'
]

def load_rows(path):
    with open(path,'r',newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def write_rows(path, rows, fieldnames):
    with open(path,'w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def build_features(input_path):
    # Aggregates
    user_counts = defaultdict(int)
    merchant_counts = defaultdict(int)
    user_amount_sum = defaultdict(float)
    merchant_amount_sum = defaultdict(float)
    output_rows = []
    for row in load_rows(input_path):
        ts = int(row['timestamp']) if row.get('timestamp') else 0
        dt = datetime.utcfromtimestamp(ts)
        amount = float(row.get('amount',0.0))
        user_id = row['user_id']
        merchant_id = row['merchant_id']
        user_counts[user_id] += 1
        merchant_counts[merchant_id] += 1
        user_amount_sum[user_id] += amount
        merchant_amount_sum[merchant_id] += amount
        avg_user = user_amount_sum[user_id]/user_counts[user_id]
        avg_merch = merchant_amount_sum[merchant_id]/merchant_counts[merchant_id]
        engineered = {
            'transaction_id': row.get('transaction_id',''),
            'user_id': user_id,
            'merchant_id': merchant_id,
            'device_id': row.get('device_id',''),
            'timestamp': ts,
            'amount': amount,
            'label': row.get('label',0),
            'hour': dt.hour,
            'is_weekend': int(dt.weekday()>=5),
            'log_amount': math.log1p(amount),
            'user_tx_count': user_counts[user_id],
            'merchant_tx_count': merchant_counts[merchant_id],
            'avg_user_amount': round(avg_user,2),
            'avg_merchant_amount': round(avg_merch,2)
        }
        output_rows.append(engineered)
    return output_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    rows = build_features(args.input)
    write_rows(args.output, rows, FEATURE_COLUMNS)
    print(f"Wrote {len(rows)} feature rows to {args.output}")

if __name__ == '__main__':
    main()
