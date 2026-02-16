"""Simple rule-based decision engine for fraud prevention.

This turns a risk score and transaction attributes into an explicit
prevention decision: APPROVE, REVIEW, or DECLINE.

It is intentionally lightweight so it can be extended later with
velocity checks, blacklists, customer segments, etc.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any


@dataclass
class DecisionResult:
    transaction_id: str
    user_id: str | None
    amount: float
    risk_score: float
    risk_category: str
    decision: str
    reasons: List[str]
    actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Thresholds can be tuned or externalised later
# These are demo defaults; in a real system they'd come from
# experiments and business input.
HIGH_RISK_THRESHOLD = 0.85
MEDIUM_RISK_THRESHOLD = 0.6
HIGH_AMOUNT = 1000.0
MEDIUM_AMOUNT = 500.0


def categorise_risk(score: float) -> str:
    if score >= HIGH_RISK_THRESHOLD:
        return "high"
    if score >= MEDIUM_RISK_THRESHOLD:
        return "medium"
    return "low"


def evaluate_transaction(tx: Dict[str, Any]) -> DecisionResult:
    """Apply simple prevention rules to a transaction.

    Expected tx keys (all optional except id and amount):
      - id: transaction identifier
      - user_id: customer identifier
      - amount: numeric amount
      - risk_score: model probability in [0,1]

        The rules are deliberately simple:
            - DECLINE transactions that are both risky and large, or
                extremely high risk regardless of amount
            - REVIEW medium-risk or high-amount transactions
            - otherwise APPROVE
    """

    tx_id = str(tx.get("id") or "tx-unknown")
    user_id = tx.get("user_id")
    try:
        amount = float(tx.get("amount", 0.0))
    except Exception:
        amount = 0.0
    try:
        score = float(tx.get("risk_score", 0.0))
    except Exception:
        score = 0.0

    risk_cat = categorise_risk(score)
    reasons: List[str] = []
    actions: List[str] = []

    decision = "APPROVE"

    # Decline only when the transaction is clearly risky:
    #   - score above high threshold, regardless of amount
    if score >= HIGH_RISK_THRESHOLD:
        decision = "DECLINE"
        reasons.append(
            f"Decline: model risk score {score:.2f} is in the high-risk band (>= {HIGH_RISK_THRESHOLD:.2f}), "
            f"indicating a high probability of fraud."
        )
        if amount >= HIGH_AMOUNT:
            reasons.append(
                f"The amount {amount:.2f} is also high (>= {HIGH_AMOUNT:.2f}), which strengthens the decision to block this transaction."
            )
        actions.append("BLOCK_TRANSACTION")

    # Review when either the model is medium‑risk or the amount is
    # large, but we don't have enough evidence to block outright.
    elif score >= MEDIUM_RISK_THRESHOLD or amount >= HIGH_AMOUNT or amount >= MEDIUM_AMOUNT:
        decision = "REVIEW"
        if MEDIUM_RISK_THRESHOLD <= score < HIGH_RISK_THRESHOLD:
            reasons.append(
                f"Review: model risk score {score:.2f} falls in the medium-risk band "
                f"[{MEDIUM_RISK_THRESHOLD:.2f}, {HIGH_RISK_THRESHOLD:.2f}), so it is not clearly safe."
            )
        if amount >= HIGH_AMOUNT:
            reasons.append(
                f"The transaction amount {amount:.2f} is high (>= {HIGH_AMOUNT:.2f}); even with a non-high risk score, "
                "this warrants a manual check instead of automatic approval."
            )
        elif MEDIUM_AMOUNT <= amount < HIGH_AMOUNT:
            reasons.append(
                f"The transaction amount {amount:.2f} is moderate (between {MEDIUM_AMOUNT:.2f} and {HIGH_AMOUNT:.2f}), "
                "so combined with the risk score we flag it for review rather than auto-approve or block."
            )
        actions.append("ROUTE_TO_MANUAL_REVIEW")

    else:
        decision = "APPROVE"
        reasons.append(
            f"Approve: model risk score {score:.2f} is below the review threshold {MEDIUM_RISK_THRESHOLD:.2f} "
            f"and amount {amount:.2f} is below {MEDIUM_AMOUNT:.2f}, so the transaction is treated as low risk."
        )
        actions.append("ALLOW")

    return DecisionResult(
        transaction_id=tx_id,
        user_id=str(user_id) if user_id is not None else None,
        amount=amount,
        risk_score=score,
        risk_category=risk_cat,
        decision=decision,
        reasons=reasons,
        actions=actions,
    )
