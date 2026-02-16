"""Fusion logic implementing P(fraud|x,g) = Σ w_m(x) * f_m(x,g)
"""
import numpy as np

def fuse(prob_dict, weight_dict):
    # prob_dict: {'rf':p1,'xgb':p2,'gnn':p3,'ae':p4}
    total = 0.0
    for k,v in prob_dict.items():
        w = weight_dict.get(k, 0.0)
        total += w * v
    return max(0.0, min(1.0, total))
