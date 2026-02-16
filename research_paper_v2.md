# Integrating SHAP with Graph Neural Networks for Interpretable Real-Time Payment Fraud Detection

**Nagarjun Gowda K N**  
Department of Computer Science and Engineering  
B M S Institute of Technology and Management  
Bengaluru, India 560064  
Email: nagarjungo@gmail.com

## Abstract

The increasing sophistication of financial fraud necessitates detection systems that are both accurate and interpretable. This paper presents a framework that integrates SHAP (SHapley Additive exPlanations) with Graph Neural Networks (GNNs) to meet explainability needs in real-time payment systems. The approach combines ensemble machine learning with multi-modal explanation generation, incorporating feature-level SHAP attributions, graph-based relational analysis, and temporal pattern signals. We evaluate the framework on a high-fidelity synthetic banking dataset bundled with this artifact (80k/10k/10k train/valid/test; ~1.4–1.6% fraud rate) and outline external validation on IEEE-CIS. The system targets high AUC-ROC and strong AUPRC under class imbalance while keeping average per-transaction latency near ~200 ms on CPU-only deployments. We provide an Article 13 (EU AI Act) compliance mapping with concrete audit fields and operational guidance.

**Index Terms**—Explainable AI, Fraud Detection, Graph Neural Networks, SHAP, Financial Cybersecurity, Real-time Systems, Interpretable ML, EU AI Act

## I. INTRODUCTION

Digital payments continue to grow rapidly, accompanied by increasingly coordinated fraud. While ensemble ML and deep models deliver strong detection, their opacity hinders compliance, analyst trust, and governance. Regulations such as the EU AI Act demand transparency for high-risk AI systems, including sufficiently detailed information to understand model outputs and their basis.

This work bridges performance and interpretability with a practical, modular framework. Contributions:

1. Unified architecture integrating SHAP with GNN (GraphSAGE) for relational fraud patterns.
2. Real-time explanation path with caching and load-aware approximation to keep latency bounded.
3. Multi-modal explanations combining feature attribution, graph structure, and temporal context.
4. Empirical evaluation on an included synthetic dataset and guidance for external datasets.
5. Regulatory compliance mapping to EU AI Act Article 13 with reproducible audit artifacts.

## II. RELATED WORK

### A. Explainable AI in Finance

SHAP provides theoretically grounded feature attributions via Shapley values [1]. While effective, exact computation is expensive; practical systems use KernelSHAP/TreeSHAP with sampling and caching. LIME [2] offers local surrogate explanations but may be unstable under sampling.

### B. Graph-Based Fraud Detection

GNNs capture relational patterns central to fraud rings and mule networks. Surveys (e.g., Zhou et al. [3]) show applicability to financial graphs but note limited transparency. Attention and post-hoc tools offer partial insight; combining model-agnostic SHAP with graph structure remains underexplored.

### C. Real-time Systems

Real-time fraud detection requires low latency and stable throughput. Commercial systems emphasize speed, yet detailed explanations often lag. Streaming architectures (Kafka/Flink) and incremental features are common building blocks.

## III. METHODOLOGY

### A. Architecture Overview

Microservices design:

- Stream ingestion (extensible to Kafka/Flink; demo uses Flask SSE)
- Feature service (transaction aggregates + dynamic graph features)
- Detection engine (RF/XGB + GraphSAGE)
- Explanation module (KernelSHAP + graph/community analysis)
- Compliance interface (audit trail + Article 13 mapping)

### B. Graph and Features

We form a temporal heterogeneous graph G = (V,E,T,A) over accounts, devices, merchants, and IPs. Dynamic features include temporal degree centrality CD(v), PageRank PR(v), clustering coefficient CC(v), neighborhood entropy E(N(v)), and burstiness T_burst(v). These augment traditional signals (amount, channel, geolocation, device/IP stability).

### C. Ensemble Model

We combine model scores with adaptive weights: P(fraud|x,g)=∑_m w_m(x,t)·f_m(x,g), m∈{RF, XGB, GNN}. GraphSAGE aggregates neighbor embeddings; edge features (amount, Δt, merchant category) support link/edge-risk variants.

### D. SHAP Explanations (KernelSHAP with Caching)

We use KernelSHAP sampling weights with a background distribution D_b, solving a weighted linear system to estimate φ. Hierarchical caching (transaction/user/global) and memoization reduce recomputation on recurring patterns. Explanations include:

- Feature attributions (top-k with sign and magnitude)
- Graph context (community membership, bridge edges, modularity)
- Temporal signals (burstiness, periodicity proxies)

### E. Graph-Specific Views

Community detection (e.g., Louvain) highlights coordinated clusters. We report modularity Q and identify bridging nodes/edges connecting suspect groups to the broader graph.

### F. Real-time Optimizations

- Incremental graph updates and lazy evaluation
- Selective/early-exit ensemble under load
- Parallel explanation generation with priority tiers
- Latency-aware trimming while meeting Article 13 minimums

## IV. DATASETS

### A. Included Synthetic Dataset (This Artifact)

Path: `data/raw/synthetic_transactions/`  
Splits and stats (computed): train.csv 80,000 rows (fraud rate ≈ 1.40%), valid.csv 10,000 (≈ 1.56%), test.csv 10,000 (≈ 1.55%).  
Columns: `timestamp, account_id, counterparty_id, device_id, ip_address, merchant_id, amount, currency, channel, label, region`  
Fraud scenarios embedded: rings/cycles, device/IP reuse, regional pockets, light drift. This dataset powers all end-to-end demos (API, SSE, dashboard).

### B. IEEE-CIS (External)

Widely used card-not-present benchmark (~590k+ rows; ~3–4% fraud). Not bundled due to license/size. Instructions: download from Kaggle, map fields to our schema (amount, device/IP proxies if available), and rerun the pipeline.

### C. Private/Banking Data (Out of Scope Here)

Where prior work referenced larger private datasets, this artifact substitutes the included synthetic set to ensure reproducibility and data safety. The methods are compatible with larger graphs given appropriate compute.

## V. EVALUATION

### A. Metrics

We emphasize class-imbalance-robust metrics: AUC-ROC, AUPRC, F1 at cost-sensitive thresholds, and calibration (Brier score, reliability plots). Accuracy is de-emphasized.

### B. Baselines and Targets

Typical ordering observed across fraud tasks: XGB ≥ RF > LR; GNN adds lift in ring/coordinated settings. Our target envelope for the included synthetic set is high AUC-ROC (≥0.95) and strong AUPRC, with per-transaction explanation latencies kept near ~200 ms on CPU-only runs. Exact scores depend on featurization and thresholding; a reproduction harness is provided.

### C. Reproducibility

- Generate/confirm data: `scripts/generate_synthetic_data.py` (already populated).
- Compute dataset stats: `python scripts/compute_dataset_stats.py`
- Run end-to-end services (prediction API, gateway with SSE, dashboard) as per README.
- Optional baseline training/eval: extend `ml-engine/pipelines/` or add a light sklearn/XGB script for AUC/AUPRC.

## VI. EXPLANATION QUALITY AND COMPLIANCE

We evaluate:

- Faithfulness: correlation between feature rank and ablation impact
- Stability: similarity of top-k features for near neighbors
- Analyst comprehension: clarity of top-5 factors and graph context

### Article 13 (EU AI Act) Mapping

We provide a practical checklist and audit fields in the artifact (see `scripts/` and service responses). Highlights:

- Basis for decision: top-k SHAP attributions with signs
- Main reasons & thresholds: decision threshold, score, margin
- Data reference & lineage: IDs, timestamps, feature sources
- Accuracy/reliability: confidence intervals (where applicable), calibration
- Human oversight: high-risk routing and override surfaces

Note: We report “coverage” of Article 13 items via an internal rubric (not a legal certification). Institutions should seek formal legal review.

## VII. CASE STUDY (SYNTHETIC FRAUD RING)

On the included test split, simulated collusion appears as dense subgraphs with shared device/IP/merchant ties. The graph view identifies communities with elevated modularity; SHAP highlights features such as burstiness and repeated counterparty links. Combined, these guide rapid analyst action (blocking cluster rather than isolated events).

## VIII. DISCUSSION AND LIMITATIONS

- Scale & performance: Very large graphs require distributed updates and GPU acceleration.
- Labels & drift: Delayed/noisy labels affect thresholds; add drift detectors and recalibration.
- Explanations under load: Use tiered detail levels; ensure minimum Article 13 content at peak.
- Compliance: Provide organization-specific policies and documented oversight processes.

## IX. CONCLUSION

We present a practical, explainable fraud framework that pairs SHAP with GNNs for relational insight while maintaining real-time responsiveness. The artifact includes a runnable pipeline, synthetic dataset, live API/gateway/dashboard, and a compliance checklist to accelerate adoption in regulated settings.

## ACKNOWLEDGMENTS

We acknowledge PyTorch Geometric, SHAP, scikit-learn, Flask, and community datasets. The dataset in this artifact is synthetic and safe for experimentation.

## REFERENCES

[1] S. M. Lundberg and S.-I. Lee, “A Unified Approach to Interpreting Model Predictions,” NeurIPS 2017.  
[2] M. T. Ribeiro, S. Singh, and C. Guestrin, “Why Should I Trust You?” KDD 2016.  
[3] Z. Zhou et al., “Graph Neural Networks: A Review of Methods and Applications,” AI Open, 2020.

## APPENDIX A: ARTICLE 13 CHECKLIST (PRACTICAL FIELDS)

| Requirement          | Field(s) in Artifact                 | Notes                                      |
| -------------------- | ------------------------------------ | ------------------------------------------ |
| System purpose       | README, service docs                 | Decision support for fraud screening       |
| Basis for decision   | Top-k SHAP, score, threshold         | Included in responses (configurable)       |
| Main reasons         | Top-5 features with business context | Dashboard/API text blocks                  |
| Data reference       | IDs, timestamps, feature sources     | Logged per decision                        |
| Accuracy/reliability | AUC/AUPRC, calibration notes         | Reported via scripts/plots                 |
| Limitations          | Discussion section                   | Class imbalance, drift, latency trade-offs |
| Human oversight      | High-risk routing guidance           | Integrate with analyst queues              |
| Rights & contact     | Organization policy hook             | To be filled per deployment                |

## APPENDIX B: REPRODUCTION COMMANDS (Windows cmd)

```cmd
:: Compute dataset stats
python scripts\compute_dataset_stats.py

:: Start prediction API (port 5001)
python prediction-api\run.py

:: Start API gateway (port 5000)
python api-gateway\app\main.py

:: Build frontend and start dashboard (port 3000)
cd frontend && npm run build && cd ..
python dashboard-service\app\main.py
```
