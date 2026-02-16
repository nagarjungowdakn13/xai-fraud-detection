"""GNN Training Pipeline for Fraud Detection

This script expects a CSV file with columns:
user_id, merchant_id, amount, timestamp, label

It builds a transaction graph and trains a GraphSAGE model for edge (interaction) fraud classification.

Usage (Windows CMD):
> set DATA_PATH=transactions.csv
> python ml-engine\pipelines\gnn_training_pipeline.py --data %DATA_PATH% --epochs 20

"""
import argparse
import csv
import time
from pathlib import Path
from typing import List, Dict

try:
    import torch
    from torch import nn
    from torch_geometric.nn import SAGEConv
    from torch_geometric.data import Data
except ImportError as e:
    raise ImportError("Torch / Torch Geometric not installed. Install with: pip install torch torch-geometric (plus torch-scatter/torch-sparse if required).") from e
from typing import Any, Dict, Tuple


class GraphSAGEFraudDetector(nn.Module):
    def __init__(self, in_dim: int = 32, hidden_dim: int = 64, num_layers: int = 2):
        super().__init__()
        self.convs = nn.ModuleList()
        last_dim = in_dim
        for _ in range(num_layers):
            conv = SAGEConv(last_dim, hidden_dim)
            self.convs.append(conv)
            last_dim = hidden_dim
        self.head = nn.Linear(last_dim * 2, 1)

    def forward(self, x, edge_index, edge_pairs):
        for conv in self.convs:
            x = conv(x, edge_index).relu()
        src = x[edge_pairs[:, 0]]
        dst = x[edge_pairs[:, 1]]
        edge_repr = torch.cat([src, dst], dim=1)
        logits = self.head(edge_repr).squeeze(-1)
        return logits


def build_graph(transactions) -> Tuple[Data, torch.Tensor, torch.Tensor]:
    id_map: Dict[Any, int] = {}
    edges = []
    labels = []
    for t in transactions:
        u = t['user_id']
        m = t['merchant_id']
        if u not in id_map:
            id_map[u] = len(id_map)
        if m not in id_map:
            id_map[m] = len(id_map)
        uid = id_map[u]
        mid = id_map[m]
        edges.append([uid, mid])
        labels.append(t.get('label', 0))
    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    num_nodes = len(id_map)
    x = torch.randn((num_nodes, 32))  # Placeholder: replace with real engineered features
    data = Data(x=x, edge_index=edge_index)
    edge_pairs = edge_index.t()
    return data, edge_pairs, torch.tensor(labels, dtype=torch.float32)


def load_transactions(path: Path) -> List[Dict]:
    rows = []
    with path.open('r', newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            # Normalize / cast
            rows.append({
                'user_id': r['user_id'],
                'merchant_id': r['merchant_id'],
                'label': int(r.get('label', 0))
            })
    return rows


def split_edges(edge_pairs, labels, train_ratio=0.8):
    total = edge_pairs.shape[0]
    train_size = int(total * train_ratio)
    indices = torch.randperm(total)
    train_idx = indices[:train_size]
    val_idx = indices[train_size:]
    return edge_pairs[train_idx], labels[train_idx], edge_pairs[val_idx], labels[val_idx]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True, help='Path to transactions CSV')
    parser.add_argument('--epochs', type=int, default=10)
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        raise FileNotFoundError(f'Dataset not found: {data_path}')

    transactions = load_transactions(data_path)
    pyg_data, edge_pairs, labels = build_graph(transactions)
    train_pairs, train_labels, val_pairs, val_labels = split_edges(edge_pairs, labels)

    model = GraphSAGEFraudDetector()

    # Train
    start_train = time.time()
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = torch.nn.BCEWithLogitsLoss()

    for epoch in range(1, args.epochs + 1):
        optimizer.zero_grad()
        logits = model(pyg_data.x, pyg_data.edge_index, train_pairs)
        loss = criterion(logits, train_labels.float())
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            preds = (logits.sigmoid() > 0.5).float()
            acc = (preds == train_labels).float().mean().item()
        if epoch % 2 == 0:
            print(f"[Epoch {epoch}] train_loss={loss.item():.4f} train_acc={acc:.4f}")

    train_time = time.time() - start_train

    # Validate
    model.eval()
    with torch.no_grad():
        val_logits = model(pyg_data.x, pyg_data.edge_index, val_pairs)
        val_preds = (val_logits.sigmoid() > 0.5).float()
        val_acc = (val_preds == val_labels).float().mean().item()

    # Latency measurement (single inference batch)
    start_inf = time.time()
    _ = model(pyg_data.x, pyg_data.edge_index, val_pairs)
    latency_ms = (time.time() - start_inf) * 1000

    print({
        'train_time_sec': train_time,
        'validation_accuracy': val_acc,
        'inference_latency_ms': latency_ms,
        'num_edges_total': int(edge_pairs.shape[0])
    })

    # Save model
    torch.save(model.state_dict(), 'gnn_fraud_detector.pt')
    print('Model saved to gnn_fraud_detector.pt')


if __name__ == '__main__':
    main()
