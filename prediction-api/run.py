from flask import Flask, request, jsonify
import math
import hashlib
from datetime import datetime


class ExplanationBuilder:
    """Lightweight local explanation builder for demo purposes.

    This avoids importing the full ml-engine stack and simply returns
    a payload with feature attributions and some metadata so the
    dashboard can always display explanations.
    """

    def build(self, probabilities, feature_attributions, graph_context, meta):
        """Build an explanation payload with human- and tech-friendly views.

        The goal is to provide:
          - a plain-language summary for non-technical users
          - structured feature attributions for analysts/engineers
        """

        # Base payload
        payload = {
            "timestamp": int(datetime.utcnow().timestamp()),
            "probabilities": probabilities,
            "feature_attributions": feature_attributions,
            "graph_context": graph_context,
            "meta": meta,
        }

        # Derive a simple risk band from the score (if available)
        score = None
        try:
            score = float(probabilities.get("ensemble"))  # type: ignore[arg-type]
        except Exception:
            score = None

        if score is not None:
            if score >= 0.85:
                risk_band = "high"
            elif score >= 0.6:
                risk_band = "medium"
            else:
                risk_band = "low"
        else:
            risk_band = "unknown"

        # Friendly names for demo features (index-based)
        friendly_definitions = {
            0: {
                "name": "Transaction amount",
                "description": (
                    "Higher transaction amounts tend to increase risk, especially when "
                    "they are unusual for this customer or context."
                ),
            },
            1: {
                "name": "Recent behaviour pattern",
                "description": (
                    "This captures how recent activity differs from typical behaviour. "
                    "Unusual spikes or patterns can push risk up."
                ),
            },
            2: {
                "name": "Network / account context",
                "description": (
                    "Signals from linked devices, IPs or accounts. "
                    "Connections to previously risky entities can increase risk."
                ),
            },
        }

        # Build enriched feature info and determine top contributors
        feature_info = {}
        sorted_feats = sorted(
            feature_attributions.items(),
            key=lambda kv: abs(kv[1]),
            reverse=True,
        )

        top_positive = []
        top_negative = []

        for name, value in sorted_feats:
            idx = None
            try:
                # Expect names like "feat_0", "feat_1", ...
                idx = int(str(name).split("_")[1])
            except Exception:
                idx = None

            base_def = friendly_definitions.get(
                idx,
                {
                    "name": str(name),
                    "description": "Model input feature.",
                },
            )

            direction = "increases risk" if value > 0 else "reduces risk"

            feature_info[name] = {
                "name": base_def["name"],
                "description": base_def["description"],
                "direction": direction,
                "attribution": float(value),
            }

            if value > 0:
                top_positive.append(feature_info[name])
            elif value < 0:
                top_negative.append(feature_info[name])

        # Build a short plain-language explanation using top contributors
        def _summarise_features(items, limit=2):
            if not items:
                return ""
            names = [it["name"] for it in items[:limit]]
            if len(names) == 1:
                return names[0]
            return ", ".join(names[:-1]) + " and " + names[-1]

        positives_txt = _summarise_features(top_positive)
        negatives_txt = _summarise_features(top_negative)

        if risk_band == "high":
            band_text = "The model sees this transaction as HIGH risk. "
        elif risk_band == "medium":
            band_text = "The model sees this transaction as MEDIUM risk. "
        elif risk_band == "low":
            band_text = "The model sees this transaction as LOW risk. "
        else:
            band_text = "The model could not clearly determine the risk level. "

        human_parts = [band_text]
        if positives_txt:
            human_parts.append(
                f"The main factors pushing the risk UP are: {positives_txt}. "
            )
        if negatives_txt:
            human_parts.append(
                f"Factors that help LOWER the risk include: {negatives_txt}. "
            )

        human_summary = "".join(human_parts).strip()

        technical_summary = (
            "Feature attributions show how each input feature contributes "
            "numerically to the model score. Positive values increase the "
            "fraud probability, negative values decrease it."
        )

        payload["feature_info"] = feature_info
        payload["summary"] = {
            "human_readable": human_summary,
            "technical": technical_summary,
            "risk_band": risk_band,
        }

        payload["hash"] = hashlib.sha256(str(payload).encode("utf-8")).hexdigest()
        return payload

app = Flask(__name__)

# Simple stub model probability (replace with real ensemble call)
def model_score(features):
    # Placeholder: logistic-like transform of mean
    if not features:
        return 0.5
    s = sum(features) / len(features)
    return 1 / (1 + math.exp(-s))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    features = data.get('features', [])
    score = model_score(features)
    return jsonify({'score': score})

@app.route('/explain', methods=['POST'])
def explain():
    data = request.get_json(force=True)
    features = data.get('features', [])
    graph_ctx = data.get('graph_context', {'neighbors': [], 'community': None})
    score = model_score(features)
    builder = ExplanationBuilder()
    # Construct a minimal unified explanation payload
    explanation = builder.build(
        probabilities={'ensemble': score},
        feature_attributions={f'feat_{i}': float(v) for i, v in enumerate(features)},
        graph_context=graph_ctx,
        meta={'version': '0.1.0', 'mode': 'demo'}
    )
    return jsonify({'score': score, 'explanation': explanation})

if __name__ == '__main__':
    # Disable reloader for stable background runs on Windows
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)