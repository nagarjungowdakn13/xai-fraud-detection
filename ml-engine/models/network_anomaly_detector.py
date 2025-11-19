# In ml-engine/models/network_anomaly_detector.py
class NetworkAnomalyXAI:
    def __init__(self):
        self.autoencoder = self._build_anomaly_detector()
        self.shap_explainer = shap.DeepExplainer(self.autoencoder)
    
    def explain_network_anomaly(self, network_traffic):
        """Explain anomalies in network traffic patterns"""
        # Detect anomaly
        reconstruction_error = self.autoencoder.predict(network_traffic)
        is_anomaly = reconstruction_error > self.threshold
        
        # Generate explanation
        shap_values = self.shap_explainer.shap_values(network_traffic)
        
        return {
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': float(reconstruction_error),
            'contributing_features': self._rank_network_features(shap_values),
            'temporal_pattern': self._analyze_temporal_behavior(network_traffic)
        }