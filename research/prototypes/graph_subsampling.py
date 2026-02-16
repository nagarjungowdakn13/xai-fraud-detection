"""Graph Subsampling Strategies (Placeholder)"""
import random

def sample_nodes(nodes, fraction=0.5):
    k = int(len(nodes)*fraction)
    return random.sample(list(nodes), k)
