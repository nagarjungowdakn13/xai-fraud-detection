# Benchmark & Evaluation Guide

This directory hosts scripts and artifacts for statistically rigorous evaluation.

## Files

- `evaluation.py`: Metric and confidence interval computation utilities.
- `raw_output_template.csv`: Template for storing a single fold's predictions.

## Running Synthetic Demo

```cmd
python -c "from benchmark.evaluation import example_demo; example_demo()" > benchmark/demo_run.log
```

Produces:

- `benchmark/demo_predictions.csv`: synthetic fold predictions
- Metrics JSON printed to stdout (redirected to log above)

## Recommended Experiment Workflow

1. Prepare dataset: `data/transactions.csv` with columns `user_id,merchant_id,amount,timestamp,label`.
2. Implement K-fold driver script (e.g., `benchmark/run_kfold.py`).
3. For each fold:
   - Train baseline + GNN models.
   - Generate probability outputs for validation set.
   - Call `evaluate_predictions(y_true, y_prob)`.
   - Save raw outputs using `save_raw_outputs()`.
4. Aggregate fold metrics into `benchmark/aggregate_metrics.json`.
5. Compute mean, std, 95% CIs; add to publication appendix.

## Integrity & Reproducibility Checklist

- Record random seed per fold.
- Log model hyperparameters.
- Store SHA256 for each predictions file.
- Capture environment: Python version, library versions (`pip freeze > benchmark/env_requirements.txt`).

## Extending Statistical Tests

- McNemar's Test: Evaluate disagreement between two classifiers (to add).
- DeLong Test: Compare ROC-AUC variance (future implementation).

## Plot Suggestions (Future)

- Reliability diagram (calibration).
- PR and ROC curves per fold + mean curve overlay.
- SHAP distribution summaries.

## Caution

No real metrics should be published until this workflow is executed on the target production-scale dataset. All placeholder numbers in root README remain illustrative.
