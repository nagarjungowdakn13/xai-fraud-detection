"""Compute basic statistics for the synthetic_transactions dataset.

Prints, for each split (train/valid/test):
- number of transactions
- number of frauds (label==1)
- fraud rate in percent

This is used to populate the dataset statistics table in the paper.
"""
from pathlib import Path

import pandas as pd


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    root = base / "data" / "raw" / "synthetic_transactions"
    if not root.exists():
        raise SystemExit(f"Synthetic dataset not found at {root}")
    rows = []
    for split in ("train", "valid", "test"):
        path = root / f"{split}.csv"
        if not path.exists():
            rows.append({"split": split, "error": f"missing file {path}"})
            continue
        df = pd.read_csv(path)
        n = len(df)
        fraud = int(df["label"].sum()) if "label" in df.columns else 0
        rate = 100.0 * fraud / n if n else 0.0
        row = {
            "split": split,
            "transactions": n,
            "fraud_count": fraud,
            "fraud_rate_pct": round(rate, 3),
        }
        rows.append(row)

    # Print to stdout for quick inspection
    for row in rows:
        print(row)

    # Also persist to a small text file for later retrieval
    out_path = base / "synthetic_stats.txt"
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(str(row) + "\n")
    print(f"Wrote stats to {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
