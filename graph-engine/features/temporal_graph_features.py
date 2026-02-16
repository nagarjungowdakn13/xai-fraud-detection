"""Temporal Graph Feature Computations (Placeholders)

Implements time-decayed PageRank, temporal degree centrality, clustering coefficient, neighborhood entropy, betweenness centrality (simplified).

These are lightweight approximations; replace with optimized incremental variants for production scale.
"""
import math
import networkx as nx
from collections import Counter

DECAY_HALF_LIFE_SEC = 3600  # one hour


def time_decay_weight(delta_seconds: float) -> float:
    # Exponential decay based on elapsed time
    return 0.5 ** (delta_seconds / DECAY_HALF_LIFE_SEC)


def temporal_degree_centrality(G: nx.Graph, now_ts: int, edge_timestamps: dict) -> dict:
    scores = Counter()
    for (u,v), ts in edge_timestamps.items():
        w = time_decay_weight(now_ts - ts)
        scores[u] += w
        scores[v] += w
    return scores


def time_decayed_pagerank(G: nx.Graph, edge_timestamps: dict, now_ts: int, alpha: float = 0.85) -> dict:
    weighted = nx.DiGraph()
    for (u,v), ts in edge_timestamps.items():
        w = time_decay_weight(now_ts - ts)
        if weighted.has_edge(u,v):
            weighted[u][v]['weight'] += w
        else:
            weighted.add_edge(u,v, weight=w)
    return nx.pagerank(weighted, alpha=alpha, weight='weight')


def clustering_coefficients(G: nx.Graph) -> dict:
    return nx.clustering(G)


def neighborhood_entropy(G: nx.Graph) -> dict:
    ent = {}
    for n in G.nodes():
        neighbors = list(G.neighbors(n))
        degs = [G.degree(x) for x in neighbors]
        if not degs:
            ent[n] = 0.0
            continue
        total = sum(degs)
        probs = [d/total for d in degs]
        e = -sum(p*math.log(p+1e-9) for p in probs)
        ent[n] = e
    return ent


def betweenness(G: nx.Graph, k: int = None) -> dict:
    # Approximate betweenness if k provided
    return nx.betweenness_centrality(G, k=k) if k else nx.betweenness_centrality(G)
