class CreditCardFraudXAI:
    def explain_credit_card_fraud(self, transaction):
        """XAI specifically for credit card fraud detection"""
        prediction = self.fraud_model.predict(transaction)
        explainer = shap.LinearExplainer(self.fraud_model, self.training_data)
        
        # Generate comprehensive explanation
        explanation = {
            'risk_score': float(prediction[0]),
            'shap_explanation': explainer.shap_values(transaction),
            'rule_based_explanations': self._apply_business_rules(transaction),
            'temporal_context': self._analyze_transaction_timing(transaction),
            'behavioral_context': self._analyze_user_behavior(transaction['user_id'])
        }
        
        return explanation