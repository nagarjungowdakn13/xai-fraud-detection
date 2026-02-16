"""Build a simple transaction graph edgelist from a dataset split.

Reads the train split created by scripts/generate_synthetic_data.py and produces:
- graph_outputs/edgelist.csv with columns: src,dst
- graph_outputs/nodes.csv with columns: node_id,original_id,type

Usage (Windows CMD):
  python scripts\build_graph_from_dataset.py --name synthetic_transactions --split train
"""
import argparse
from pathlib import Path
import pandas as pd


def build_graph(df: pd.DataFrame):
    # Expect columns: account_id, merchant_id
    accounts = df['account_id'].astype(str).unique().tolist()
    merchants = df['merchant_id'].astype(str).unique().tolist()

    node_map = {}
    nodes = []
    nid = 0
    for a in accounts:
        node_map[("account", a)] = nid
        nodes.append((nid, a, "account"))
        nid += 1
    for m in merchants:
        node_map[("merchant", m)] = nid
        nodes.append((nid, m, "merchant"))
        nid += 1

    edges = []
    for _, row in df[['account_id', 'merchant_id']].iterrows():
        src = node_map[("account", str(row['account_id']))]
        dst = node_map[("merchant", str(row['merchant_id']))]
        edges.append((src, dst))

    return nodes, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', type=str, default='synthetic_transactions')
    ap.add_argument('--split', type=str, default='train', choices=['train', 'valid', 'test'])
    args = ap.parse_args()

    base = Path(__file__).resolve().parents[1]
    split_path = base / 'data' / 'raw' / args.name / f'{args.split}.csv'
    if not split_path.exists():
        raise FileNotFoundError(f"Dataset split not found: {split_path}")

    df = pd.read_csv(split_path)
    required = {'account_id', 'merchant_id'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns {missing} in {split_path}")

    nodes, edges = build_graph(df)

    out_dir = base / 'graph_outputs'
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes_df = pd.DataFrame(nodes, columns=['node_id', 'original_id', 'type'])
    edges_df = pd.DataFrame(edges, columns=['src', 'dst'])

    nodes_df.to_csv(out_dir / 'nodes.csv', index=False)
    edges_df.to_csv(out_dir / 'edgelist.csv', index=False)

    print({
        'nodes': len(nodes_df),
        'edges': len(edges_df),
        'nodes_path': str(out_dir / 'nodes.csv'),
        'edges_path': str(out_dir / 'edgelist.csv'),
    })


if __name__ == '__main__':
    main()
