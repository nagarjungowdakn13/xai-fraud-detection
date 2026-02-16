"""Dataset setup utility
- Validates presence of required columns
- Writes a standardized split manifest (train/valid/test)
Usage:
  python scripts/dataset_setup.py --input path/to.csv --name my_dataset --split 0.8 0.1 0.1
  or provide explicit files with --train/--valid/--test
"""
import argparse
import os
import shutil
from pathlib import Path
import pandas as pd

REQUIRED_COLS = [
    'timestamp','account_id','counterparty_id','device_id','ip_address',
    'merchant_id','amount','currency','channel','label'
]


def ensure_cols(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


def write_manifest(base: Path, name: str, train: Path, valid: Path, test: Path):
    manifest = base / 'data' / 'manifest.yaml'
    base_raw = base / 'data' / 'raw' / name
    base_raw.mkdir(parents=True, exist_ok=True)
    # copy files
    shutil.copy2(train, base_raw / 'train.csv')
    shutil.copy2(valid, base_raw / 'valid.csv')
    shutil.copy2(test,  base_raw / 'test.csv')
    # append or write manifest
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
    print(f"Dataset {name} registered with manifest at {manifest}")


def split_and_register(base: Path, df: pd.DataFrame, name: str, split):
    ensure_cols(df)
    n = len(df)
    n_train = int(n * split[0])
    n_valid = int(n * split[1])
    train_df = df.iloc[:n_train]
    valid_df = df.iloc[n_train:n_train+n_valid]
    test_df  = df.iloc[n_train+n_valid:]
    tmp = base / 'tmp_dataset'
    tmp.mkdir(exist_ok=True)
    train_p = tmp / 'train.csv'; train_df.to_csv(train_p, index=False)
    valid_p = tmp / 'valid.csv'; valid_df.to_csv(valid_p, index=False)
    test_p  = tmp / 'test.csv';  test_df.to_csv(test_p, index=False)
    write_manifest(base, name, train_p, valid_p, test_p)
    shutil.rmtree(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=str, help='Path to single CSV to split')
    ap.add_argument('--name', type=str, required=True)
    ap.add_argument('--split', type=float, nargs=3, default=[0.8,0.1,0.1])
    ap.add_argument('--train', type=str)
    ap.add_argument('--valid', type=str)
    ap.add_argument('--test', type=str)
    args = ap.parse_args()
    base = Path(__file__).resolve().parents[1]

    if args.train and args.valid and args.test:
        for pth in [args.train, args.valid, args.test]:
            df = pd.read_csv(pth)
            ensure_cols(df)
        write_manifest(base, args.name, Path(args.train), Path(args.valid), Path(args.test))
        return

    if not args.input:
        ap.error('Provide --input or explicit --train/--valid/--test')
    df = pd.read_csv(args.input)
    split_and_register(base, df, args.name, args.split)

if __name__ == '__main__':
    main()
