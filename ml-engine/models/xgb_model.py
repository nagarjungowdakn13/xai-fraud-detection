"""XGBoost Wrapper (Placeholder)
Install xgboost before using.
"""
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

class XGBFraudModel:
    def __init__(self, **kwargs):
        if XGBClassifier is None:
            raise ImportError("xgboost not installed. Please pip install xgboost.")
        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric='logloss',
            **kwargs
        )

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict_proba(self, X):
        return self.model.predict_proba(X)[:,1]
