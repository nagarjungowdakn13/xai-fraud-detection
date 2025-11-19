# In ml-engine/xai/explainable_fraud_detector.py
class ExplainableFraudDetector:
    def generate_shap_explanations(self, transaction_data):
        """Generate SHAP explanations for fraud predictions"""
        explainer = shap.TreeExplainer(self.ensemble_model)
        shap_values = explainer.shap_values(transaction_data)
        
        return {
            'base_value': explainer.expected_value,
            'shap_values': shap_values.tolist(),
            'feature_importance': self._calculate_feature_importance(shap_values),
            'decision_plot': self._generate_decision_plot(shap_values, transaction_data)
        }