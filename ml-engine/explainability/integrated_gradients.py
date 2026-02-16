"""Integrated Gradients for Node Embeddings (Simplified)
"""
import torch

def integrated_gradients(model, embeddings, target_index, steps: int = 20):
    baseline = torch.zeros_like(embeddings)
    scaled = [baseline + (float(i)/steps)*(embeddings-baseline) for i in range(steps+1)]
    grads = []
    for emb in scaled:
        emb.requires_grad_(True)
        out = model(emb)[target_index]
        out.backward()
        grads.append(emb.grad.detach())
    avg_grads = torch.stack(grads).mean(dim=0)
    return (embeddings - baseline) * avg_grads
