# Metrics & Statistical Formulas Reference

## 1. ROC Curve & AUC

Given scores s_i and binary labels y_i ∈ {0,1}. Sort instances by descending score.
TPR(t) = TP(t) / (TP(t) + FN(t))
FPR(t) = FP(t) / (FP(t) + TN(t))
ROC-AUC approximated via trapezoidal rule over FPR axis.

### 1.1 DeLong Variance (Binary Case)

DeLong (1988) expresses AUC as U-statistic.
Let positive set P, negative set N with sizes m, n.
Define V*i = (1/n) Σ*{j∈N} φ(s*i, s_j) for i∈P
Define W_j = (1/m) Σ*{i∈P} φ(s*i, s_j) for j∈N
φ(a,b)=1 if a>b, 0.5 if a=b, 0 otherwise.
AUC = (1/m) Σ*{i∈P} V*i = (1/n) Σ*{j∈N} W_j
Var(AUC) = (Var(V)/m) + (Var(W)/n)
Where Var(V)= (1/(m-1)) Σ (V_i - mean(V))^2
and Var(W)= (1/(n-1)) Σ (W_j - mean(W))^2
Z-test comparing two AUCs: z = (AUC1 - AUC2)/sqrt(Var1 + Var2 - 2\*Cov12)

## 2. Precision, Recall, F1

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 _ Precision _ Recall / (Precision + Recall)
Precision@K: Sort by score; consider top K; Precision@K = TP_K / K.

## 3. PR-AUC (Average Precision)

AP = Σ*{n} (R_n - R*{n-1}) \* P_interp(n)
Interpolated precision often chosen as max precision for recall ≥ R_n.

## 4. Brier Score

BS = (1/N) Σ (p_i - y_i)^2
Decompose: BS = Reliability - Resolution + Uncertainty.

## 5. Expected Calibration Error (ECE)

Partition scores into B bins: B*k = {i | p_i in interval k}.
ECE = Σ*{k=1..B} (|B_k|/N) \* |acc(B_k) - conf(B_k)|
acc(B_k)= (1/|B_k|) Σ y_i ; conf(B_k)= (1/|B_k|) Σ p_i.

## 6. Population Stability Index (PSI)

For bins b with expected proportion e_b and current proportion c_b:
PSI = Σ (c_b - e_b) \* ln(c_b / e_b)
Heuristic interpretation: <0.1 stable, 0.1-0.25 moderate shift, >0.25 significant.

## 7. Kolmogorov-Smirnov (KS) Test (Binary Scores)

KS = max_t |F_1(t) - F_0(t)| where F_1 and F_0 are CDFs of scores for positives and negatives.

## 8. Bootstrapped Confidence Intervals

Given metric M over dataset D.
Repeat B times:

- Sample D_b by stratified sampling with replacement.
- Compute M_b.
  CI (α) ≈ quantiles at α/2 and 1-α/2 of {M_b}.
  Bias-corrected & accelerated (BCa) optional for skew.

## 9. McNemar Test

For two classifiers A,B on same instances.
Contingency counts: n01 (A wrong, B correct), n10 (A correct, B wrong).
Chi-square ≈ (|n01 - n10| - 1)^2 / (n01 + n10)
Use continuity correction; p-value from χ^2 with 1 d.o.f.

## 10. Threshold Optimization (Cost-Sensitive)

Objective: Maximize Expected Utility.
EU(t) = Σ*{i} [ y_i * w_tp * 1*{s*i≥t} + (1 - y_i) * (-w_fp) * 1*{s_i≥t} ] / N
Search t over candidate thresholds (e.g., score quantiles).

## 11. Class Imbalance Adjustments

Balanced Accuracy = (Recall_pos + Recall_neg)/2.
G-Mean = sqrt(Recall_pos \* Recall_neg).

## 12. Ensemble Fusion (Weighted Probabilities)

Given model probabilities p_k(x) and weights w_k (Σ w_k=1):
P_ensemble(x) = Σ w_k p_k(x)
Optionally calibrate with isotonic or temperature scaling.

## 13. Integrated Gradients (Simplified)

IG*i = (x_i - x'\_i) \* (1/m) Σ*{l=1..m} ∂F(x' + l/m (x - x'))/∂x_i
Baseline x' often zero or mean feature vector.

## 14. Fast SHAP Approximation

Target original Shapley value φ*i.
Approximate via sampling permutations Π:
φ̂_i = (1/|Π|) Σ*{π∈Π} [F(S_i^π ∪ {i}) - F(S_i^π)]
With early stopping if variance below ε or max samples reached.

## 15. Confidence Interval for AUC (Normal Approximation)

CI ≈ AUC ± z\_{α/2} \* sqrt(Var(AUC))
Var(AUC) from DeLong or Hanley–McNeil (simpler, less accurate).

## 16. Expected Loss Under Threshold

Given cost matrix: C_FP, C_FN.
Expected Cost(t) = C_FP _ FP(t) + C_FN _ FN(t)
Select t minimizing Expected Cost.

---

Placeholder formulas will be validated against implementation; any divergence triggers documentation update.
