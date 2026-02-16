.PHONY: start-all stop-all build logs clean

# === Core Orchestration ===

start-all:
	docker-compose up -d

stop-all:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

migrate:
	docker-compose exec backend python migrate.py

test:
	docker-compose exec backend python -m pytest tests/

load-test:
	./scripts/load_test.sh

deploy-prod:
	./scripts/deploy_prod.sh

scale-up:
	docker-compose up -d --scale backend=3 --scale ml-engine=2

scale-down:
	docker-compose up -d --scale backend=1 --scale ml-engine=1

# === Experiment & Evaluation Targets ===

# Chronological stratified k-fold evaluation (placeholder dataset)
kfold:
	docker-compose exec ml-engine python benchmark/run_kfold.py

# Ablation study runner
ablation:
	docker-compose exec ml-engine python benchmark/ablation.py

# Performance / latency synthetic benchmark
perf:
	docker-compose exec ml-engine python load/performance_test.py

# Generate LaTeX / markdown performance tables
tables:
	docker-compose exec ml-engine python benchmark/generate_tables.py

# Reliability diagram & calibration metrics
reliability:
	docker-compose exec ml-engine python benchmark/reliability.py

# DeLong ROC comparison
delong:
	docker-compose exec ml-engine python benchmark/delong.py

# Drift monitoring one-off report
drift-monitor:
	docker-compose exec ml-engine python monitoring/drift.py

# Train full ensemble stack (base models + meta learner)
train-ensemble:
	docker-compose exec ml-engine python ml-engine/pipelines/train_ensemble.py

# Multi-modal explanation demo (single transaction)
explain:
	docker-compose exec ml-engine python ml-engine/explainability/explanation_builder.py || echo "Use API endpoint /explain once integrated"

# Export frozen environment manifests
export-env:
	docker-compose exec ml-engine python scripts/export_env.py

# === Data & Fairness Utilities ===
dataset-setup:
	docker-compose exec ml-engine python scripts/dataset_setup.py --input data/raw/sample_transactions/train.csv --name sample_transactions

features:
	docker-compose exec ml-engine python feature_engineering/feature_pipeline.py

build-graph:
	docker-compose exec ml-engine python graph-engine/build_graph.py data/raw/sample_transactions/train.csv --out graph.edgelist

calibrate:
	docker-compose exec ml-engine python ml-engine/calibration/calibrate.py --preds ensemble_outputs/fold_predictions/fold_0.csv --method isotonic --out calibrated_fold_0.csv

fairness:
	docker-compose exec ml-engine python benchmark/fairness.py ensemble_outputs/predictions_baseline.csv --group region --threshold 0.5

thresholds:
	docker-compose exec ml-engine python benchmark/thresholds.py ensemble_outputs/fold_predictions/fold_0.csv --c_fp 1.0 --c_fn 5.0

# Generate synthetic dataset with fraud patterns
gen-data:
	docker-compose exec ml-engine python scripts/generate_synthetic_data.py --name synthetic_transactions --n_tx 20000 --fraud_rate 0.01

# One-shot end-to-end synthetic experiment (containers must be running)
e2e-synthetic:
	$(MAKE) start-all
	$(MAKE) gen-data-100k
	$(MAKE) baseline-predict
	$(MAKE) reliability
	$(MAKE) fairness
	$(MAKE) thresholds
	$(MAKE) train-ensemble
	$(MAKE) tables

# Generate a larger dataset with mild drift and 5 regions
gen-data-100k:
	docker-compose exec ml-engine python scripts/generate_synthetic_data.py --name synthetic_transactions --n_tx 100000 --fraud_rate 0.01 --drift_day 20 --regions 5

# Train a quick baseline on dataset and produce predictions with group columns
baseline-predict:
	docker-compose exec ml-engine python scripts/score_baseline_on_dataset.py --name synthetic_transactions --out ensemble_outputs/predictions_baseline.csv
