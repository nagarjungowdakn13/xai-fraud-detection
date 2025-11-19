from py2neo import Graph, Node, Relationship, NodeMatcher
import networkx as nx
from community import community_louvain
import numpy as np

class FraudGraphIntelligence:
    def __init__(self, graph):
        self.graph = graph
        self.matcher = NodeMatcher(graph)
    
    def detect_fraud_rings(self, transaction_data):
        """Detect fraud rings using community detection"""
        
        # Create or update graph with new transaction
        self._update_graph(transaction_data)
        
        # Community detection for fraud rings
        communities = self._detect_communities()
        
        # Multi-hop analysis
        suspicious_paths = self._find_suspicious_paths(transaction_data)
        
        return {
            "communities": communities,
            "suspicious_paths": suspicious_paths,
            "risk_score": self._calculate_graph_risk(transaction_data)
        }
    
    def _update_graph(self, transaction):
        """Update graph with new transaction data"""
        # Create nodes
        user_node = Node("User", id=transaction["user_id"], 
                        risk_score=transaction.get("risk_score", 0))
        merchant_node = Node("Merchant", id=transaction["merchant_id"])
        device_node = Node("Device", id=transaction.get("device_id"))
        
        # Create relationships
        made_tx = Relationship(user_node, "MADE_TRANSACTION", merchant_node,
                             amount=transaction["amount"],
                             timestamp=transaction["timestamp"])
        
        used_device = Relationship(user_node, "USED_DEVICE", device_node)
        
        # Merge into graph
        self.graph.merge(user_node, "User", "id")
        self.graph.merge(merchant_node, "Merchant", "id")
        self.graph.merge(device_node, "Device", "id")
        self.graph.merge(made_tx)
        self.graph.merge(used_device)
    
    def _detect_communities(self):
        """Detect communities using Louvain method"""
        # Convert to NetworkX for community detection
        nx_graph = self._to_networkx()
        
        if len(nx_graph.nodes) > 0:
            communities = community_louvain.best_partition(nx_graph)
            return communities
        return {}
    
    def _find_suspicious_paths(self, transaction, max_hops=3):
        """Find suspicious money flow paths"""
        query = """
        MATCH path = (start:User {id: $user_id})-[*1..3]-(end)
        WHERE ALL(r IN relationships(path) WHERE r.timestamp >= $recent_timestamp)
        RETURN path, 
               reduce(risk = 0, n in nodes(path) | risk + n.risk_score) as path_risk
        ORDER BY path_risk DESC
        LIMIT 10
        """
        
        result = self.graph.run(query, 
                              user_id=transaction["user_id"],
                              recent_timestamp=transaction["timestamp"] - 3600000)
        
        return [dict(record) for record in result]
    
    def _calculate_graph_risk(self, transaction):
        """Calculate graph-based risk score"""
        # Implementation for graph risk scoring
        return 0.0
    
    def _to_networkx(self):
        """Convert Neo4j graph to NetworkX for analysis"""
        nx_graph = nx.Graph()
        
        # Add nodes and edges from Neo4j
        # Implementation details...
        
        return nx_graph