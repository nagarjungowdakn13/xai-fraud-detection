import shap
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import json

class SHAPExplainer:
    def __init__(self, model, feature_names: List[str], model_type: str = 'tree'):
        self.model = model
        self.feature_names = feature_names
        self.model_type = model_type
        self.explainer = None
        self._initialize_explainer()

    def _initialize_explainer(self):
        """Initialize the SHAP explainer based on model type."""
        if self.model_type == 'tree':
            self.explainer = shap.TreeExplainer(self.model)
        elif self.model_type == 'linear':
            self.explainer = shap.LinearExplainer(self.model)
        elif self.model_type == 'kernel':
            self.explainer = shap.KernelExplainer(self.model.predict, self.background_data)
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def explain_instance(self, instance: np.ndarray) -> Dict[str, Any]:
        """Explain a single instance."""
        if self.model_type == 'kernel':
            shap_values = self.explainer.shap_values(instance)
        else:
            shap_values = self.explainer.shap_values(instance)

        # For tree models, we might get a list of arrays (for multi-class). In binary classification, we take the second one.
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        # Convert to list for JSON serialization
        feature_importance = {
            feature: {
                'shap_value': float(shap_values[i]),
                'feature_value': float(instance[i])
            }
            for i, feature in enumerate(self.feature_names)
        }

        # Generate summary plot (optional, for logging or visualization)
        self._generate_summary_plot(shap_values, instance)

        return feature_importance

    def _generate_summary_plot(self, shap_values, instance):
        """Generate and save a SHAP summary plot for the instance."""
        plt.figure()
        shap.waterfall_plot(self.explainer.expected_value, shap_values, instance, 
                            feature_names=self.feature_names, show=False)
        plt.savefig('shap_waterfall.png', bbox_inches='tight')
        plt.close()

    def explain_batch(self, instances: np.ndarray) -> List[Dict[str, Any]]:
        """Explain a batch of instances."""
        return [self.explain_instance(instance) for instance in instances]

class GraphSHAPExplainer:
    def __init__(self, graph_model, node_embedding_model):
        self.graph_model = graph_model
        self.node_embedding_model = node_embedding_model

    def explain_node(self, node_id: str) -> Dict[str, Any]:
        """Explain the graph model's prediction for a node."""
        # This is a placeholder for graph explanation techniques.
        # We can use methods such as GNNExplainer or SHAP for graphs.
        # For now, we return a mock explanation.
        return {
            "node_id": node_id,
            "influential_neighbors": self._get_influential_neighbors(node_id),
            "community": self._get_community(node_id),
            "embedding_similarity": self._get_embedding_similarity(node_id)
        }

    def _get_influential_neighbors(self, node_id: str) -> List[Dict]:
        """Get the most influential neighbors for the node."""
        # Mock data for now
        return [
            {"node_id": "123", "influence": 0.8},
            {"node_id": "456", "influence": 0.6}
        ]

    def _get_community(self, node_id: str) -> str:
        """Get the community the node belongs to."""
        return "Community_1"

    def _get_embedding_similarity(self, node_id: str) -> List[Dict]:
        """Get the most similar nodes based on embeddings."""
        return [
            {"node_id": "789", "similarity": 0.9},
            {"node_id": "101", "similarity": 0.85}
        ]

# Integrated explainer that combines both model and graph explanations
class IntegratedExplainer:
    def __init__(self, model_explainer: SHAPExplainer, graph_explainer: GraphSHAPExplainer):
        self.model_explainer = model_explainer
        self.graph_explainer = graph_explainer

    def explain_transaction(self, transaction_data: np.ndarray, node_id: str) -> Dict[str, Any]:
        """Explain a transaction by combining model and graph explanations."""
        model_explanation = self.model_explainer.explain_instance(transaction_data)
        graph_explanation = self.graph_explainer.explain_node(node_id)

        return {
            "model_explanation": model_explanation,
            "graph_explanation": graph_explanation,
            "combined_risk_score": self._combine_risk_scores(model_explanation, graph_explanation)
        }

    def _combine_risk_scores(self, model_explanation: Dict, graph_explanation: Dict) -> float:
        """Combine risk scores from model and graph explanations."""
        # Simple combination for now - can be more sophisticated
        model_risk = abs(sum([feat['shap_value'] for feat in model_explanation.values()]))
        graph_risk = len(graph_explanation['influential_neighbors']) / 10.0
        return (model_risk + graph_risk) / 2.0