"""DeLong test implementation for comparing ROC AUC of two classifiers.
Usage: python benchmark/delong.py preds1.csv preds2.csv
Each CSV needs columns: y_true, y_prob
"""
import sys
import numpy as np
import pandas as pd
from math import sqrt
from scipy.stats import norm


def compute_ground_truth_statistics(ground_truth: np.ndarray):
    assert set(np.unique(ground_truth)) <= {0,1}
    return ground_truth == 1, ground_truth == 0


def auc_variances(scores: np.ndarray, labels: np.ndarray):
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    m = len(pos)
    n = len(neg)
    # Pairwise comparison matrix
    cmp = np.subtract.outer(pos, neg)
    phi = (cmp > 0).astype(float) + 0.5 * (cmp == 0)
    V = phi.mean(axis=1)  # per positive
    W = phi.mean(axis=0)  # per negative
    auc = V.mean()
    var_v = np.var(V, ddof=1)
    var_w = np.var(W, ddof=1)
    var_auc = var_v / m + var_w / n
    return auc, var_auc, V, W


def delong_covariance(V1, W1, V2, W2):
    # Covariance between two AUC estimators sharing same sample
    cov_v = np.cov(V1, V2, ddof=1)[0,1] / len(V1)
    cov_w = np.cov(W1, W2, ddof=1)[0,1] / len(W1)
    return cov_v + cov_w


def delong_test(y_true: np.ndarray, scores1: np.ndarray, scores2: np.ndarray):
    auc1, var1, V1, W1 = auc_variances(scores1, y_true)
    auc2, var2, V2, W2 = auc_variances(scores2, y_true)
    cov12 = delong_covariance(V1, W1, V2, W2)
    diff = auc1 - auc2
    var_diff = var1 + var2 - 2 * cov12
    if var_diff <= 0:
        # Numerical fallback
        var_diff = 1e-12
    z = diff / sqrt(var_diff)
    p = 2 * (1 - norm.cdf(abs(z)))
    return {
        "auc1": auc1,
        "auc2": auc2,
        "diff": diff,
        "z": z,
        "p_value": p,
        "var_auc1": var1,
        "var_auc2": var2,
        "cov_auc": cov12,
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python benchmark/delong.py preds1.csv preds2.csv")
        return
    df1 = pd.read_csv(sys.argv[1])
    df2 = pd.read_csv(sys.argv[2])
    for df in (df1, df2):
        if not {'y_true','y_prob'}.issubset(df.columns):
            raise ValueError("Each CSV must contain y_true,y_prob")
    if not np.array_equal(df1['y_true'].values, df2['y_true'].values):
        raise ValueError("Ground truth labels must align")
    y = df1['y_true'].values.astype(int)
    r = delong_test(y, df1['y_prob'].values, df2['y_prob'].values)
    for k,v in r.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    main()
