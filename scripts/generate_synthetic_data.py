"""Generate synthetic fraud transaction datasets.
- Simulates accounts, merchants, devices, IPs
- Fraud patterns: rings, risky merchants, device novelty, high-amount spikes
- Optional concept drift after a cutoff date

Usage (examples):
  python scripts/generate_synthetic_data.py --name synthetic_transactions --n_tx 20000 --fraud_rate 0.01
  python scripts/generate_synthetic_data.py --name synthetic_transactions --n_tx 50000 --drift_day 20

Outputs:
  data/raw/<name>/{train,valid,test}.csv and updates data/manifest.yaml
"""
import argparse
import os
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

REQUIRED_COLS = [
    'timestamp','account_id','counterparty_id','device_id','ip_address',
    'merchant_id','amount','currency','channel','label'
]

CHANNELS = ['web','mobile','pos']
CURRENCY = ['USD']


def rand_ip(rng):
    return f"{rng.integers(1,223)}.{rng.integers(0,255)}.{rng.integers(0,255)}.{rng.integers(1,254)}"


def generate_dataset(n_tx: int, seed: int = 42, fraud_rate: float = 0.01, drift_day: int | None = None, regions: int = 5):
    rng = np.random.default_rng(seed)
    n_accounts = max(1000, n_tx // 20)
    n_merchants = max(100, n_tx // 200)
    n_devices = max(500, n_tx // 50)

    accounts = np.array([f"A{i}" for i in range(1, n_accounts+1)])
    merchants = np.array([f"M{i}" for i in range(1, n_merchants+1)])
    devices = np.array([f"D{i}" for i in range(1, n_devices+1)])

    # Assign base profiles
    acct_device = rng.choice(devices, size=n_accounts)
    acct_ip = np.array([rand_ip(rng) for _ in range(n_accounts)])
    # Regions for fairness slices
    region_labels = np.array(['NA','EU','APAC','LATAM','MEA'][:max(1, regions)])
    acct_region = rng.choice(region_labels, size=n_accounts, p=(np.ones(len(region_labels))/len(region_labels)))

    # Risky merchant subset (higher fraud propensity)
    risky_merchants = set(rng.choice(merchants, size=max(5, n_merchants//10), replace=False))

    # Fraud rings: choose k rings, each with 10-30 accounts
    k_rings = max(3, n_accounts // 300)
    ring_members = set()
    rings = []
    remaining_accounts = accounts.copy()
    rng.shuffle(remaining_accounts)
    idx = 0
    for _ in range(k_rings):
        size = int(rng.integers(10, 30))
        grp = remaining_accounts[idx: idx+size]
        if len(grp) == 0:
            break
        rings.append(set(grp))
        ring_members.update(grp)
        idx += size

    # Time range
    start = datetime(2025,1,1,8,0,0)
    # Simulate transactions day-wise
    rows = []
    for t in range(n_tx):
        # Timestamp with gentle growth
        day = t // max(1, n_tx // 30)
        time = start + timedelta(days=int(day), minutes=int(rng.integers(0, 60*24)))

        # Concept drift: after drift_day, increase risky merchant prevalence and shift amount distribution
        drift_multiplier = 1.0
        if drift_day is not None and day >= drift_day:
            drift_multiplier = 1.5

        a = rng.choice(accounts)
        # Counterparty: sometimes another account (P2P), else synthetic counterparty id
        if rng.random() < 0.3:
            c = rng.choice(accounts)
        else:
            c = f"EXT{rng.integers(1, 200000)}"

        # Device usage: mostly assigned device, sometimes new device (novelty)
        if rng.random() < 0.9:
            d = acct_device[int(a[1:]) - 1]
        else:
            d = rng.choice(devices)

        a_idx = int(a[1:]) - 1
        ip = acct_ip[a_idx]
        region = acct_region[a_idx]
        m = rng.choice(merchants)

        # Amount distribution with occasional spikes; drift increases scale
        base_amt = np.abs(rng.normal(40.0 * drift_multiplier, 35.0 * drift_multiplier))
        spike = rng.random() < 0.02
        amount = base_amt + (rng.uniform(200, 1500) if spike else 0.0)
        amount = round(float(amount), 2)

        channel = rng.choice(CHANNELS, p=[0.5, 0.4, 0.1])
        currency = 'USD'

        # Fraud probability drivers
        p = fraud_rate
        if m in risky_merchants:
            p += 0.02 * drift_multiplier
        if d not in acct_device:  # extremely rare; fallback check
            p += 0.01
        elif d != acct_device[int(a[1:]) - 1]:  # new device for this account
            p += 0.02
        if amount > 500:
            p += 0.03
        # Ring interactions: account transacts with ring member counterparty
        in_ring = any(a in ring for ring in rings)
        cp_in_ring = any((c in ring) if isinstance(c, str) and c.startswith('A') else False for ring in rings)
        if in_ring and cp_in_ring:
            p += 0.2
        label = int(rng.random() < min(max(p, 0.0), 0.9))

        rows.append((
            time.isoformat() + 'Z', a, c, d, ip, m, amount, currency, channel, label, region
        ))

    df = pd.DataFrame(rows, columns=REQUIRED_COLS + ['region'])
    # Sort by time for chronological splits
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df


def write_splits(base: Path, name: str, df: pd.DataFrame):
    raw_dir = base / 'data' / 'raw' / name
    raw_dir.mkdir(parents=True, exist_ok=True)
    n = len(df)
    n_train = int(n * 0.8)
    n_valid = int(n * 0.1)
    train_df = df.iloc[:n_train]
    valid_df = df.iloc[n_train:n_train+n_valid]
    test_df  = df.iloc[n_train+n_valid:]
    train_df.to_csv(raw_dir / 'train.csv', index=False)
    valid_df.to_csv(raw_dir / 'valid.csv', index=False)
    test_df.to_csv(raw_dir / 'test.csv', index=False)

    # Update manifest
    manifest = base / 'data' / 'manifest.yaml'
    content = f"""
# Auto-generated manifest for {name}
dataset_name: {name}
version: 0.1.0
paths:
  train: data/raw/{name}/train.csv
  valid: data/raw/{name}/valid.csv
  test:  data/raw/{name}/test.csv
"""
    with open(manifest, 'a', encoding='utf-8') as f:
        f.write('\n' + content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', type=str, default='synthetic_transactions')
    ap.add_argument('--n_tx', type=int, default=20000)
    ap.add_argument('--fraud_rate', type=float, default=0.01)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--drift_day', type=int, default=None)
    ap.add_argument('--regions', type=int, default=5)
    args = ap.parse_args()

    base = Path(__file__).resolve().parents[1]
    df = generate_dataset(args.n_tx, seed=args.seed, fraud_rate=args.fraud_rate, drift_day=args.drift_day, regions=args.regions)
    write_splits(base, args.name, df)
    print(f"Generated dataset '{args.name}' with {len(df)} rows under data/raw/{args.name}")

if __name__ == '__main__':
    main()
