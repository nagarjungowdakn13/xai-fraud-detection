"""Fraud Ring Detector (Placeholder)
Identifies communities and returns those above size threshold.
"""
import networkx as nx

def detect_rings(G, min_size=5):
    communities = nx.algorithms.community.greedy_modularity_communities(G)
    rings = [list(c) for c in communities if len(c)>=min_size]
    return {'num_rings': len(rings), 'rings': rings[:3]}
