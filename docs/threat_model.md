# Threat Model: Fraud Detection System

## 1. Scope

Components covered: data ingestion, feature engineering, model training pipeline, ensemble inference API, explanation subsystem, audit logging, graph processing layer.
Out-of-scope: External identity verification services, payment processor internal infrastructure.

## 2. Assets

| Asset            | Description                         | Sensitivity                 |
| ---------------- | ----------------------------------- | --------------------------- |
| Transaction Data | Raw financial events                | High (PII/financial)        |
| Feature Store    | Engineered features & graph metrics | Medium                      |
| Model Artifacts  | Trained parameters / weights        | Medium                      |
| Explanations     | Context + attributions              | Medium (may leak insights)  |
| Audit Logs       | Immutable investigation trail       | High                        |
| Graph Structures | Account-device-merchant relations   | High (relationship privacy) |

## 3. Adversaries & Capabilities

| Adversary     | Goal                    | Capability                                        |
| ------------- | ----------------------- | ------------------------------------------------- |
| Fraudster     | Evade detection         | Transaction crafting, multi-account orchestration |
| Data Poisoner | Degrade model           | Inject mislabeled benign/fraud patterns           |
| Insider       | Extract sensitive info  | Elevated system access                            |
| API Harvester | Reverse engineer model  | High-rate querying, explanation scraping          |
| Competitor    | Gain strategic insights | Passive monitoring of outputs                     |

## 4. Attack Vectors

1. Evasion: Structured low-velocity fraud to mimic legitimate patterns.
2. Graph Manipulation: Fabricated account/device linkages to dilute risk centrality.
3. Data Poisoning: Bulk low-risk fraudulent seeds mislabeled as benign.
4. Model Extraction: Query fuzzing + explanation correlation to approximate decision boundary.
5. Explanation Abuse: Reconstruct sensitive feature distributions via repeated explain calls.
6. Replay / Duplicate: Reuse successful transaction patterns at scale.

## 5. Security Controls

| Control             | Type          | Mitigates                              |
| ------------------- | ------------- | -------------------------------------- |
| Rate Limiting       | Prevent abuse | Model extraction, explanation scraping |
| Anomaly Thresholds  | Detection     | Poisoning ingestion anomalies          |
| Explanation Hashing | Integrity     | Tampering & repudiation                |
| Drift Monitoring    | Observability | Slow poisoning, concept shift          |
| Access Segmentation | Authorization | Insider misuse                         |
| Audit Logging       | Forensic      | Post-incident reconstruction           |
| Version Pinning     | Integrity     | Malicious model replacement            |

## 6. Residual Risks

- Adaptive adversaries may exploit feature importance disclosure.
- Low-signal incremental poisoning hard to distinguish from natural drift.
- Graph-based collusion detection still prototype; false negatives possible.

## 7. Mitigations Roadmap

| Item                            | Priority | Description                                      |
| ------------------------------- | -------- | ------------------------------------------------ |
| Differential Privacy Review     | Medium   | Limit sensitive leakage via explanations         |
| Adversarial Simulation Harness  | High     | Stress-test model under crafted attack scenarios |
| Robust Training (Noise / MixUp) | Medium   | Increase resilience to poisoning                 |
| Graph Anomaly Ensembles         | Medium   | Combine structural + temporal embeddings         |
| Canary Features                 | Low      | Detect unnatural distribution shifts             |

## 8. Incident Response

1. Detect anomaly (latency spike, PSI > threshold, unexplained AUC drop).
2. Triage logs & isolate suspicious input batches.
3. Snapshot current model + feature store.
4. Roll back to last trusted model version.
5. Execute forensic pipeline (reconstruct timeline, affected accounts).
6. Prepare compliance report & mitigation patch.

## 9. Monitoring Signals

| Signal                  | Metric               | Alert Threshold                   |
| ----------------------- | -------------------- | --------------------------------- |
| Distribution Shift      | PSI                  | >0.25 (moderate), >0.4 (critical) |
| Calibration Degradation | ECE                  | >0.06 sustained                   |
| Query Velocity          | Requests/min         | >95th percentile baseline         |
| Explanation Density     | Explains/score ratio | >0.3 abnormal                     |
| Graph Volatility        | Edge churn %         | >2× rolling avg                   |

## 10. Assumptions

- Infrastructure authentication and network segmentation handled externally.
- Labels eventually consistent; short-term delays acceptable.
- No adversarial example crafting at perturbation granularity (tabular feasibility limited).

## 11. Non-Goals

- Formal cryptographic verification of inference.
- Full privacy-preserving training (e.g., federated learning) at this stage.

## 12. Review & Updates

Quarterly security review; incident-driven immediate revision.

## 13. Disclaimer

This threat model is iterative and will evolve as real data, usage patterns, and adversarial behaviors become available.
