"""Semi-Supervised Placeholder (Pseudo-labeling)"""
import numpy as np

def pseudo_label(probabilities, threshold=0.9):
    return (np.array(probabilities) > threshold).astype(int)
