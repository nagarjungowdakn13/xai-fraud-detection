"""Multi-modal Explanation Builder
Combines SHAP, graph context, temporal features, rule-based flags.
"""
from datetime import datetime
import hashlib

class ExplanationBuilder:
    def __init__(self):
        pass

    def build(self, transaction, shap_values, graph_ctx, temporal_ctx, rules):
        payload = {
            'transaction_id': transaction.get('transaction_id'),
            'timestamp': int(datetime.utcnow().timestamp()),
            'risk_score': transaction.get('risk_score'),
            'shap_values': shap_values,
            'graph_context': graph_ctx,
            'temporal_context': temporal_ctx,
            'rules_triggered': rules,
            'version': 'v1'
        }
        h = hashlib.sha256(str(payload).encode()).hexdigest()
        payload['hash'] = h
        return payload
