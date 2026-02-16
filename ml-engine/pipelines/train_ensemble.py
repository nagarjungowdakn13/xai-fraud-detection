"""Train ensemble components (placeholder synthetic workflow).
This script demonstrates orchestrated training and saving prediction files for downstream evaluation.
Replace synthetic data generation with real feature loading in production.
"""
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression

try:
    from xgboost import XGBClassifier  # type: ignore
except Exception:
    XGBClassifier = None

SEED = 42
np.random.seed(SEED)

OUT_DIR = Path("ensemble_outputs")
OUT_DIR.mkdir(exist_ok=True)

N = 2000
F = 20
X = np.random.randn(N, F)
y = (np.random.rand(N) < 0.08).astype(int)

# Base models
rf = RandomForestClassifier(n_estimators=120, random_state=SEED, n_jobs=-1)
rf.fit(X, y)
p_rf = rf.predict_proba(X)[:,1]

if XGBClassifier:
    xgb = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8, random_state=SEED, eval_metric='logloss')
    xgb.fit(X, y)
    p_xgb = xgb.predict_proba(X)[:,1]
else:
    p_xgb = np.zeros_like(p_rf)

# Simple anomaly score placeholder (invert mean abs feature value magnitude)
ano_score = 1 - np.abs(X).mean(axis=1) / np.abs(X).mean()

# Meta learner combining predictions
stack_features = np.vstack([p_rf, p_xgb, ano_score]).T
meta = LogisticRegression(max_iter=200)
meta.fit(stack_features, y)
p_meta = meta.predict_proba(stack_features)[:,1]

auc_base = roc_auc_score(y, p_rf)
auc_meta = roc_auc_score(y, p_meta)

summary = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "seed": SEED,
    "n_samples": int(N),
    "n_features": int(F),
    "auc_random_forest": float(auc_base),
    "auc_meta": float(auc_meta),
}
with open(OUT_DIR / "ensemble_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

# K-fold predictions for evaluation
fold_dir = OUT_DIR / "fold_predictions"
fold_dir.mkdir(exist_ok=True)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
fold_idx = 0
for train_idx, test_idx in skf.split(X, y):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    rf_f = RandomForestClassifier(n_estimators=100, random_state=SEED, n_jobs=-1)
    rf_f.fit(X_train, y_train)
    p_test = rf_f.predict_proba(X_test)[:,1]
    df_out = pd.DataFrame({
        'y_true': y_test,
        'y_prob': p_test
    })
    df_out.to_csv(fold_dir / f"fold_{fold_idx}.csv", index=False)
    fold_idx += 1

print("Ensemble training complete. Summary and fold predictions written.")
