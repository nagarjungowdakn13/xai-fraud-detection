import torch
from torch import nn
from torch_geometric.nn import SAGEConv
from torch_geometric.data import Data
from typing import Dict, Any, Tuple
import time

class GraphSAGEFraudDetector(nn.Module):
    """GraphSAGE-based node/edge classification for fraud detection.

    Assumes a heterogeneous transaction graph simplified to a homogeneous graph:
    - Nodes: Users, Merchants, Devices encoded as integer ids in a single index space.
    - Edges: Interactions (user->merchant), (user->device) aggregated.
    - Labels: Provided per edge (fraud=1 / legit=0) or per node (risk class). This implementation focuses on edge classification.
    """

    def __init__(self, in_dim: int = 32, hidden_dim: int = 64, num_layers: int = 2):
        super().__init__()
        self.convs = nn.ModuleList()
        last_dim = in_dim
        for _ in range(num_layers):
            conv = SAGEConv(last_dim, hidden_dim)
            self.convs.append(conv)
            last_dim = hidden_dim
        self.head = nn.Linear(last_dim * 2, 1)  # For edge pair representation (src||dst)

    def forward(self, x, edge_index, edge_pairs):
        for conv in self.convs:
            x = conv(x, edge_index).relu()
        # Edge representation by concatenating src and dst node embeddings
        src = x[edge_pairs[:,0]]
        dst = x[edge_pairs[:,1]]
        edge_repr = torch.cat([src, dst], dim=1)
        logits = self.head(edge_repr).squeeze(-1)
        return logits


def build_graph(transactions) -> Tuple[Data, torch.Tensor]:
    """Build a PyG Data object from transaction records.
    transactions: list of dicts with keys user_id, merchant_id, device_id(optional), label
    Returns: (graph_data, edge_pairs_tensor)
    NOTE: This is a placeholder; integrate with real data loader.
    """
    # Map entity ids to contiguous indices
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
    # Random initial node features (Replace with real features: frequency, avg_amount, etc.)
    x = torch.randn((num_nodes, 32))
    data = Data(x=x, edge_index=edge_index)
    edge_pairs = edge_index.t()
    return data, edge_pairs, torch.tensor(labels, dtype=torch.float32)


def train(model: GraphSAGEFraudDetector, data: Data, edge_pairs: torch.Tensor, labels: torch.Tensor, epochs: int = 10):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.BCEWithLogitsLoss()
    model.train()
    start = time.time()
    for epoch in range(1, epochs+1):
        optimizer.zero_grad()
        logits = model(data.x, data.edge_index, edge_pairs)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()
        if epoch % 2 == 0:
            with torch.no_grad():
                preds = (logits.sigmoid() > 0.5).float()
                acc = (preds == labels).float().mean().item()
            print(f"Epoch {epoch} loss={loss.item():.4f} acc={acc:.4f}")
    latency_ms = (time.time() - start) * 1000 / epochs
    return {
        'final_loss': float(loss.item()),
        'approx_training_latency_per_epoch_ms': latency_ms
    }


def evaluate(model: GraphSAGEFraudDetector, data: Data, edge_pairs: torch.Tensor, labels: torch.Tensor):
    model.eval()
    with torch.no_grad():
        logits = model(data.x, data.edge_index, edge_pairs)
        probs = logits.sigmoid()
        preds = (probs > 0.5).float()
        acc = (preds == labels).float().mean().item()
        return {
            'accuracy': acc,
            'num_edges': int(labels.shape[0])
        }

if __name__ == '__main__':
    # Example synthetic usage
    synthetic_transactions = [
        {'user_id': 'U1', 'merchant_id': 'M1', 'label': 0},
        {'user_id': 'U2', 'merchant_id': 'M1', 'label': 1},
        {'user_id': 'U1', 'merchant_id': 'M2', 'label': 0},
        {'user_id': 'U3', 'merchant_id': 'M2', 'label': 1},
        {'user_id': 'U4', 'merchant_id': 'M3', 'label': 0},
    ]
    data, edge_pairs, labels = build_graph(synthetic_transactions)
    model = GraphSAGEFraudDetector()
    train_stats = train(model, data, edge_pairs, labels, epochs=6)
    eval_stats = evaluate(model, data, edge_pairs, labels)
    print({'train': train_stats, 'eval': eval_stats})
