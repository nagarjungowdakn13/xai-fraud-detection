"""Graph Attention Network for Fraud Edge Classification (Simplified)
"""
import torch
from torch import nn
from torch_geometric.nn import GATConv

class GATFraudDetector(nn.Module):
    def __init__(self, in_dim=32, hidden_dim=64, heads=4, num_layers=2):
        super().__init__()
        self.convs = nn.ModuleList()
        last = in_dim
        for i in range(num_layers):
            conv = GATConv(last, hidden_dim, heads=heads, concat=True)
            self.convs.append(conv)
            last = hidden_dim * heads
        self.head = nn.Linear(last*2, 1)

    def forward(self, x, edge_index, edge_pairs):
        for conv in self.convs:
            x = conv(x, edge_index).relu()
        src = x[edge_pairs[:,0]]
        dst = x[edge_pairs[:,1]]
        logits = self.head(torch.cat([src,dst], dim=1)).squeeze(-1)
        return logits
