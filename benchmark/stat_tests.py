"""Statistical Tests (Simplified)
Includes paired t-test and McNemar placeholder.
"""
import numpy as np
from math import sqrt

def paired_t_test(a,b):
    diff = np.array(a)-np.array(b)
    mean = diff.mean()
    sd = diff.std(ddof=1)
    t = mean/(sd/sqrt(len(diff))) if sd>0 else 0.0
    return {'t_stat':float(t),'mean_diff':float(mean)}

def mcnemar(contingency):
    # contingency: [[tn, fp],[fn, tp]] - misuse: for disagreement use b,c
    tn,fp = contingency[0]
    fn,tp = contingency[1]
    b = fp
    c = fn
    if b+c==0:
        return {'chi2':0.0,'p_value':1.0}
    chi2 = (abs(b-c)-1)**2/(b+c)
    return {'chi2':float(chi2),'p_value':'~approx'}
