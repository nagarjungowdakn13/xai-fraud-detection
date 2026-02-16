# Fraud Detection Enterprise

A microservices-based fraud detection platform using Flask, React, Kafka, Flink, and Neo4j.

## Project Structure

- `backend/`: Flask REST API (User Auth, Fraud Analysis, Graph Visualization)
- `frontend/`: React + Vite Dashboard
- `ml-engine/`: Machine Learning models (Fraud Detector, Anomaly Detection)
- `streaming/`: Flink jobs for real-time processing
- `docker-compose.yml`: Infrastructure orchestration

## Prerequisites

- Docker & Docker Compose
- Python 3.9+ (for local dev)
- Node.js 18+ (for local dev)

## Quick Start (Docker)

1.  Build and start all services:
    ```bash
    docker-compose up --build
    ```
2.  Access the Dashboard:
    Open [http://localhost:3000](http://localhost:3000)
3.  Access the Backend API:
    [http://localhost:5000](http://localhost:5000)

## Local Development

### Backend

1.  Navigate to `backend/`:
    ```bash
    cd backend
    ```
2.  Create virtualenv and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    # Ensure you are in the project root
    export PYTHONPATH=$PYTHONPATH:.
    python backend/app/main.py
    ```

### Frontend

1.  Navigate to `frontend/`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start dev server:
    ```bash
    npm run dev
    ```

## Features

- **Real-time Fraud Detection**: Analyzes transactions via Kafka stream.
- **Graph Analysis**: Visualizes relationships using Neo4j.
- **Dashboard**: Live alerts and statistics.
- **GNN Fraud Modeling**: GraphSAGE-based edge classification (`graph-engine/models/gnn_fraud_detector.py`) for relational fraud detection.
- **Explainable AI**: SHAP feature attributions (tree, linear, deep) + contextual rule/temporal/behavioral layers.

## Screenshots

<img width="1914" height="926" alt="Screenshot 2025-11-19 220805" src="https://github.com/user-attachments/assets/26f8f5e6-5f40-4ddc-8fcb-76d778145b26" />

<img width="1905" height="925" alt="Screenshot 2025-11-19 215313" src="https://github.com/user-attachments/assets/6da3f28e-0974-439e-b4fd-6e89bc4d5975" />

<img width="1907" height="925" alt="Screenshot 2025-11-19 220736" src="https://github.com/user-attachments/assets/babf4fa7-716b-433c-b9d2-031d96e2362b" />

<img width="1905" height="925" alt="Screenshot 2025-11-19 220751" src="https://github.com/user-attachments/assets/94b19a56-71ac-45cb-b35e-03d62030485d" />
## Research Abstract (Updated Implementation)

This platform implements an explainable, real-time fraud detection architecture combining ensemble machine learning (Isolation Forest, Random Forest, Autoencoder), streaming ingestion (Kafka + Flink), and both graph mining (Neo4j + networkx) and neural graph learning (GraphSAGE PyTorch Geometric) for relational fraud pattern discovery. The newly added GraphSAGE model performs edge-level classification over user–merchant interactions enabling learned embeddings beyond handcrafted risk scores. Explainability is delivered through SHAP-based feature attributions (tree / linear / deep variants) and contextual layers (rule-based, temporal, behavioral) for credit card and network anomaly scenarios. Fraud ring risk is enhanced via community detection plus learned relational representations. The architecture targets low latency scoring and horizontal scalability across microservices (Flask APIs, React/Vite dashboard, ML engine, streaming jobs).

## Future Work (Planned Enhancements)

- Integrate true GNN models (e.g., GraphSAGE / GAT via PyTorch Geometric) for learned relational embeddings.
- Formal latency and accuracy benchmarking on multi-million transaction datasets with reproducible experiment scripts.
- Add regulatory explanation templates (JSON schemas) aligned with audit standards (e.g., PSD2, AML).
- Expand temporal sequence modeling (LSTM / Transformer) for evolving user behavior.
- Add automated model drift monitoring and retraining triggers.

## Accuracy & Latency Claim Status

The previously stated metrics (92.1% accuracy, 185 ms average latency, 6.3% improvement over gradient boosting, 18% false positive reduction) CANNOT be validated inside this repository currently because:

- No transaction dataset (e.g., 1.2M rows CSV) is present.
- No benchmarking logs, notebooks, or saved model artifacts are provided.
- The new GNN pipeline (`ml-engine/pipelines/gnn_training_pipeline.py`) is ready for experimentation but requires a labeled dataset with columns: `user_id, merchant_id, amount, timestamp, label`.

### How to Produce Verifiable Metrics

1. Collect or load a large labeled transactions file (add to `data/transactions.csv`).
2. Run classical models (Isolation Forest, Random Forest, Autoencoder) on the same train/test split; record accuracy, precision, recall, F1, ROC-AUC.
3. Train GraphSAGE:
   ```cmd
   python ml-engine\pipelines\gnn_training_pipeline.py --data data\transactions.csv --epochs 20
   ```
4. Measure inference latency:
   - Time a batch prediction for N edges (already printed as `inference_latency_ms`).
   - Ensure environment uses production-like hardware; repeat 30 runs and take mean.
5. Compute false positive reduction: Compare FP counts baseline vs GNN.
6. Store results in `benchmark/` (CSV + README + code commit). Only then report percentages.

Until these steps are completed, treat previous numeric claims as placeholders.

## Benchmarking & Statistical Reporting Appendix

This repository now includes `benchmark/evaluation.py` which supports rigorous metric computation for imbalanced fraud datasets.

### Reportable Metrics (Per Fold)

- Confusion Matrix: TP, FP, FN, TN
- Threshold-agnostic: ROC-AUC, PR-AUC (AUPRC)
- Thresholded (default 0.5): Precision, Recall, F1, Specificity, Brier Score
- Operational Trade-offs: Precision @ fixed Recall (default 0.90), Recall @ fixed Precision (default 0.90), Precision@K (top K high-risk edges)
- Calibration: Brier score (add reliability diagrams via future plot function)

### Uncertainty Estimation

Bootstrapped percentile confidence intervals (default 1000 resamples) are produced for: Precision, Recall, F1, ROC-AUC, PR-AUC. Increase `n_bootstrap` for tighter bounds (trade-off with runtime). Always report: point estimate (mean), 95% CI [lower, upper], number of positive samples.

### Recommended Experimental Protocol

1. Fix random seeds (e.g., `SEED=42`) across data split, model init, and PyTorch/CUDA.
2. Perform stratified K-fold (e.g., K=5 or 10) maintaining fraud class ratio.
3. For each fold: train baseline models (Isolation Forest, Random Forest, Autoencoder) + GNN.
4. Collect per-fold metric JSON + raw predictions CSV via `save_raw_outputs`.
5. Aggregate metrics across folds: report mean, std dev, 95% CI.
6. Statistical Tests:
   - ROC comparison: DeLong test (external implementation needed; not yet included).
   - Paired error comparison: McNemar's test on misclassification disagreement matrix.
   - PR-AUC comparison: Bootstrap difference distribution (report p-value where proportion of differences < 0).
7. Threshold Selection: Optimize threshold for desired recall (e.g., 95%) minimizing FP cost; record threshold, resulting Precision/Recall/FPR.
8. Cost-Sensitive Evaluation: Define approximate cost matrix (False Positive vs False Negative). Report Expected Cost at chosen threshold.

### Example Metric Generation (Synthetic)

```cmd
python -c "from benchmark.evaluation import example_demo; example_demo()" > benchmark/demo_run.log
```

### Raw Output Integrity

Each predictions CSV should include SHA256 hash logged in an experiment summary to allow external verification without exposing sensitive transaction content (hash proves immutability of file).

### Minimum Disclosure for Publication

- Dataset description: size, time span, fraud ratio (%), anonymization method.
- Feature categories: behavioral, transactional, graph-derived (degree, community id), temporal aggregates.
- Model config: architecture parameters, learning rate, epochs, early stopping criteria.
- Hardware: CPU/GPU model, memory, batch sizes.
- Reproducibility: script names, command lines, seed list, software versions.

### Future Additions (Not Yet Implemented)

- DeLong test for ROC variance.
- Reliability diagram plotting utility.
- Drift tracking: population stability index (PSI) per feature.
- SHAP aggregation plots across folds.

Until these protocol steps and artifacts are committed, treat all previously reported performance numbers as illustrative rather than validated.
