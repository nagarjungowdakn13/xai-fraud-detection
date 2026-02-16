"""Meta Learner for Dynamic Weights
Uses a simple logistic regression on transaction features to produce per-model weights.
"""
import numpy as np
from sklearn.linear_model import LogisticRegression

class MetaWeightLearner:
    def __init__(self):
        self.clf = LogisticRegression(max_iter=200)
        self.model_names = ['rf','xgb','gnn','ae']

    def fit(self, X_meta, y):
        # X_meta: shape (n_samples, feature_dim)
        self.clf.fit(X_meta, y)

    def weights(self, X_meta_row):
        # Produce normalized weights from classifier probabilities (heuristic)
        base = self.clf.predict_proba([X_meta_row])[0]
        w = base / (base.sum() + 1e-9)
        return dict(zip(self.model_names, w))
