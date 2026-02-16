import json
from pathlib import Path
import pandas as pd

base = Path('data/raw/synthetic_transactions')

def describe(path: Path):
    df = pd.read_csv(path)
    cols = list(df.columns)
    fraud_rate = float(df['label'].mean()) if 'label' in df.columns else None
    return {
        'rows': int(len(df)),
        'fraud_rate': fraud_rate,
        'columns': cols
    }

def main():
    out = {}
    for name in ['train.csv','valid.csv','test.csv']:
        p = base / name
        if p.exists():
            out[name] = describe(p)
        else:
            out[name] = {'error': 'missing'}
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
