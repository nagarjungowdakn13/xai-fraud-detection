"""Transformer Encoder for Transaction Sequences (Placeholder)
"""
import torch
from torch import nn

class TransactionTransformer(nn.Module):
    def __init__(self, feature_dim=32, nhead=4, num_layers=2, dim_feedforward=128):
        super().__init__()
        encoder_layer = nn.TransformerEncoderLayer(d_model=feature_dim, nhead=nhead, dim_feedforward=dim_feedforward)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.cls_head = nn.Linear(feature_dim, 1)

    def forward(self, seq):
        # seq: (sequence_len, batch, feature_dim)
        encoded = self.encoder(seq)
        cls_token = encoded[0]  # simplistic
        return self.cls_head(cls_token).squeeze(-1)
