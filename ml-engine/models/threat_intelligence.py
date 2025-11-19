class CyberThreatXAI:
    def predict_and_explain_threats(self, security_events):
        """Predict and explain cyber threats with XAI"""
        # Threat prediction
        threat_prediction = self.threat_model.predict(security_events)
        
        # XAI explanations
        explainer = shap.TreeExplainer(self.threat_model)
        shap_values = explainer.shap_values(security_events)
        
        threat_explanation = {
            'threat_level': threat_prediction,
            'key_indicators': self._extract_key_indicators(shap_values),
            'attack_pattern': self._identify_attack_pattern(security_events),
            'confidence_scores': self._calculate_confidence(shap_values),
            'mitigation_recommendations': self._generate_mitigations(threat_prediction, shap_values)
        }
        
        return threat_explanation