"""Incremental Graph Updater

Maintains an edge timestamp dictionary and prunes entries outside a rolling window.
Use for real-time streaming updates.
"""
import time
import networkx as nx

class IncrementalGraph:
    def __init__(self, window_seconds: int = 3600):
        self.G = nx.Graph()
        self.edge_timestamps = {}
        self.window_seconds = window_seconds

    def add_transaction(self, user_id: str, merchant_id: str, ts: int = None):
        if ts is None:
            ts = int(time.time())
        self.G.add_edge(user_id, merchant_id)
        self.edge_timestamps[(user_id, merchant_id)] = ts
        self._prune(ts)

    def _prune(self, now_ts: int):
        to_remove = []
        for (u,v), ts in self.edge_timestamps.items():
            if now_ts - ts > self.window_seconds:
                to_remove.append((u,v))
        for e in to_remove:
            self.G.remove_edge(*e)
            del self.edge_timestamps[e]

    def snapshot(self):
        return self.G.copy(), dict(self.edge_timestamps)
