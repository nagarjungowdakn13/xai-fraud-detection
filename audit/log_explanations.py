"""Audit Logger for Explanations
Appends hashed explanation payloads to a ledger file.
"""
import json, time
from pathlib import Path

LEDGER_PATH = Path('audit/explanation_ledger.jsonl')

def log_explanation(expl: dict):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open('a') as f:
        entry = {'ts': int(time.time()), 'hash': expl.get('hash'), 'payload': expl}
        f.write(json.dumps(entry)+'\n')
