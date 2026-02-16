"""Build a transaction graph from CSV files.
Nodes: accounts, devices, merchants (typed); Edges: (account->merchant), (account->device), (account->counterparty)
Usage:
  python graph-engine/build_graph.py data/raw/sample_transactions/train.csv --out graph.edgelist
"""
import sys
import argparse
import pandas as pd
import networkx as nx


def build_graph(df: pd.DataFrame) -> nx.Graph:
    G = nx.Graph()
    for _, r in df.iterrows():
        a = f"acct:{r['account_id']}"
        m = f"mch:{r['merchant_id']}"
        d = f"dev:{r['device_id']}"
        c = f"acct:{r['counterparty_id']}"
        G.add_node(a, ntype='account')
        G.add_node(m, ntype='merchant')
        G.add_node(d, ntype='device')
        G.add_node(c, ntype='account')
        G.add_edge(a, m, etype='purchase')
        G.add_edge(a, d, etype='uses')
        G.add_edge(a, c, etype='transfers')
    return G


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv', type=str)
    ap.add_argument('--out', type=str, default='graph.edgelist')
    args = ap.parse_args()
    df = pd.read_csv(args.csv)
    G = build_graph(df)
    nx.write_edgelist(G, args.out, data=[('etype', str)])
    print(f"Graph saved to {args.out} with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

if __name__ == '__main__':
    main()
