# Dataset Datasheet (Placeholder)

## 1. Motivation

Goal: Support fraud risk scoring, prioritization of suspicious transactions, and analyst investigation context.
Primary tasks: Binary classification (fraud vs legitimate), anomaly scoring, graph pattern detection.

## 2. Composition

- Entities: Transactions, Accounts, Devices, IP addresses, Merchants.
- Core Transaction Fields (planned): timestamp, account_id, counterparty_id, device_id, ip_address, merchant_id, amount, currency, channel, label.
- Auxiliary Features: Geolocation (country/region), device fingerprint hash, historical velocity aggregates.
- Sensitive Attributes (potential): Geo-region, device metadata. (Will require fairness monitoring.)
- Class Distribution: Expected <1% fraud. Synthetic placeholders currently used.

## 3. Collection Process (To Be Confirmed)

- Source Systems: Payment gateway logs, user account database, device telemetry service.
- Data Capture: Append-only event ingestion with immutable transaction IDs.
- Labeling: Post-transaction review outcomes, chargebacks, manual escalations.

## 4. Preprocessing & Cleaning

| Step                     | Description                                         | Rationale            |
| ------------------------ | --------------------------------------------------- | -------------------- |
| Timestamp normalization  | Convert to UTC, derive hour_of_day, day_of_week     | Temporal consistency |
| Amount scaling           | log(amount + 1) & z-score                           | Reduce skew          |
| Categorical encoding     | Target/frequency encoding for merchant_id/device_id | High cardinality     |
| Graph feature generation | Temporal degree, decayed PageRank                   | Network behavior     |
| Imbalance handling       | Stratified folds, threshold tuning, cost weighting  | Preserve recall      |

## 5. Uses & Tasks

| Task                 | Input                            | Output                   |
| -------------------- | -------------------------------- | ------------------------ |
| Fraud classification | Engineered feature vector        | Probability score        |
| Graph anomaly        | Edge/node attributes             | Risk explanation context |
| Sequence modeling    | Ordered transactions per account | Sequence embedding       |

## 6. Distribution

- Temporal coverage: Rolling 90-day window (planned); current placeholder synthetic data.
- Geography: International (multi-region) – pending validation.

## 7. Dataset Splits

| Split            | Strategy                       | Notes                |
| ---------------- | ------------------------------ | -------------------- |
| Train            | Earliest chronological segment | Avoid leakage        |
| Validation       | Subsequent time slice          | Threshold tuning     |
| Test             | Most recent segment            | Simulates production |
| Cross-validation | Time-aware stratified k-fold   | Variance estimation  |

## 8. Quality & Integrity

- Missing Values: Device/IP sometimes absent; impute with sentinel tokens.
- Anomaly Checks: Negative amounts, duplicate transaction IDs flagged.
- Drift Monitoring: PSI & KS-test over rolling weekly windows (planned).

## 9. Ethical Considerations

- Bias Risk: Location-based or device-based false positives.
- Mitigations: Segment performance review, fairness metrics roadmap.
- PII Handling: Hash persistent identifiers; avoid raw personal data in explanations.

## 10. Access & Privacy

- Access Control: Restricted to fraud analytics & DS teams.
- Retention: Transaction logs retained per compliance policies (e.g., PCI DSS).
- Removal: Individual transaction removal only via compliance-approved process.

## 11. Provenance & Lineage

Each feature value should be traceable back to raw event + transformation pipeline commit hash.

## 12. Security Considerations

- Poisoning Risk: Tampered labels or synthetic bulk transactions.
- Countermeasures: Validation rules, anomaly detection on ingestion.

## 13. Known Gaps

- No real production dataset integrated yet.
- Fairness attributes (e.g., customer segment) not defined.
- Temporal concept drift adaptation not validated.

## 14. Update Policy

- Monthly ingestion audit.
- Quarterly schema review.
- Versioning: Maintain dataset manifest with semantic version increments.

## 15. Citation / Acknowledgments

Add appropriate source acknowledgments once real datasets integrated.

## 16. Disclaimer

This datasheet describes an anticipated dataset; current repository uses synthetic placeholders for development.
