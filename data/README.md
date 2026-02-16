# Data Directory

Place raw and processed datasets here.

Expected files (placeholders):

- `banking_transactions.csv` (anonymized 1.2M real-world dataset placeholder)
- `ieee_cis_transactions.csv` (public IEEE-CIS derived subset)
- `synthetic_transactions.csv` (generated via `synthetic_generator.py`)

Schema (minimum columns):
`transaction_id,user_id,merchant_id,device_id,timestamp,amount,currency,country,channel,label`

Fraud prevalence to be computed and appended to this README by pipeline scripts.

Anonymization recommendations:

- Hash user_id / merchant_id with SHA256 + salt.
- Strip PII (names, full addresses) before import.
- Bucket timestamp to seconds.

Chronological splits created by `scripts/make_splits.py` will produce:

- `folds/fold_<k>_train.csv`
- `folds/fold_<k>_val.csv`
