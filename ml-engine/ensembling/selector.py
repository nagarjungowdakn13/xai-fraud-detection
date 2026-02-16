"""Selective Model Activation Heuristic
Returns subset of models given quick pre-screen probability.
"""

def select_models(pre_screen_score: float):
    # If very low risk, only light models; if moderate, add RF; if high, add all.
    if pre_screen_score < 0.2:
        return ['rf']
    if pre_screen_score < 0.5:
        return ['rf','xgb']
    return ['rf','xgb','gnn','ae']
