# Model Card: Fraud Detection Ensemble

## 1. Overview

The fraud detection system is a modular ensemble combining tabular models (Random Forest, XGBoost), anomaly detectors (Isolation Forest, Autoencoder), graph neural networks (GraphSAGE, GAT), and a transaction sequence Transformer. A meta-learner fuses calibrated probabilities. Explanations are multi-modal (feature attributions, graph context, temporal patterns).

## 2. Intended Use

- Primary: Real-time scoring of financial transactions for fraud risk prioritization.
- Secondary: Analyst investigation support with context-rich explanations.
- Out-of-scope: AML regulatory filing automation, credit risk underwriting decisions, biometric verification.

## 3. Users & Personas

| Persona            | Need                       | Interface                        |
| ------------------ | -------------------------- | -------------------------------- |
| Fraud Ops Analyst  | Triage alerts              | Dashboard / Explanations API     |
| Data Scientist     | Experiment & retrain       | Training pipeline / notebooks    |
| Compliance Officer | Audit trail & transparency | Explanation logs & documentation |

## 4. Data

- Sources (planned): Transaction ledger, account profiles, device/browser fingerprints, IP geo, historical label decisions.
- Current state: Synthetic / placeholder data – real datasets not yet integrated.
- Imbalance: Expect strong class imbalance (<1% fraud); mitigation via stratified folds, threshold optimization, cost-sensitive weighting.

## 5. Performance (PLACEHOLDER)

Real metrics will be produced after integrating production datasets.
Metrics to report:

- Discrimination: ROC-AUC, PR-AUC
- Ranking: Precision@K, Recall@Fixed Precision
- Calibration: Brier Score, ECE (Expected Calibration Error)
- Latency: P50 / P95 / P99 (ms)
- Drift: PSI, KS-test over rolling windows

## 6. Evaluation Protocol

- Chronological stratified k-fold (time-aware) splitting.
- Bootstrapped confidence intervals (1,000 resamples stratified).
- Statistical comparisons: DeLong test for ROC; McNemar for paired classification; Ablation variance.

## 7. Ethical & Fairness Considerations

Potential bias from correlated demographic or geographic features. Planned mitigations:

- Sensitive attribute monitoring (if available).
- Threshold analysis per segment.
- Fairness metrics (equal opportunity difference) – future roadmap.

## 8. Safety & Security

- Adversarial vectors: Injection (crafted transactions), data poisoning, model extraction via explanation queries.
- Mitigations: Rate limiting, explanation payload hashing, drift & anomaly monitoring, adversarial pattern rules.

## 9. Limitations

- Current performance figures are NOT validated on real-world data.
- Temporal modeling and graph updates are prototype quality.
- Explainability faithfulness metrics in early stage.

## 10. Risks of Misuse

- Over-reliance on single probability score without context.
- Use outside financial domain without recalibration.
- Feedback loops if declined transactions retrain model without correction.

## 11. Maintenance & Versioning

| Component      | Update Trigger                 | Versioning Strategy                 |
| -------------- | ------------------------------ | ----------------------------------- |
| Tabular Models | Quarterly / drift detection    | Semantic (major.minor.patch)        |
| Graph Models   | Schema changes / new relations | Separate sub-version                |
| Transformer    | New sequence feature sets      | Aligned with ensemble minor version |

## 12. Monitoring Plan

- Daily drift report (PSI, KS).
- Weekly calibration check (ECE).
- Monthly performance retraining assessment.
- Alert thresholds for sudden AUC drop >5% or PSI > 0.25.

## 13. Explainability

Modalities:

1. Feature attributions (FastSHAP / TreeSHAP)
2. Graph context (neighbor risk, community tags)
3. Temporal evolution (rolling amount spikes)
4. Sequence attention (Transformer heads – planned)
   Faithfulness & stability metrics tracked in benchmark suite.

## 14. Privacy

- PII minimization planned; hashed identifiers in explanations.
- No raw personal attributes stored in audit log.

## 15. Roadmap Items

- Real dataset ingestion & validated metrics
- Full DeLong implementation (in progress)
- Calibration plots & ECE reporting
- Fairness slice metrics
- Production-grade ring detection & transformer integration

## 16. Disclaimer

This model card describes a work-in-progress system. Do not cite performance until real evaluation artifacts are generated.
