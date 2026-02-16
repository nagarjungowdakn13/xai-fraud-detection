from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import os
import json
import time
import random
import hashlib

try:
    # Simple rule-based prevention engine
    from .decision_engine import evaluate_transaction  # type: ignore
except Exception:  # pragma: no cover - fallback if relative import fails
    from decision_engine import evaluate_transaction  # type: ignore

try:
    # Optional audit logger; best-effort only
    from audit.log_explanations import log_explanation  # type: ignore
except Exception:  # pragma: no cover - if not on PYTHONPATH, ignore
    def log_explanation(_expl: dict) -> None:
        return None
try:
    from flask_cors import CORS  # type: ignore
except Exception:
    CORS = None

app = Flask(__name__)
if CORS:
    CORS(app, resources={r"/*": {"origins": "*"}})

# Service endpoints
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:5001')
TRANSACTION_SERVICE_URL = os.getenv('TRANSACTION_SERVICE_URL', 'http://transaction-service:5002')
ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://ml-service:5003')
GRAPH_SERVICE_URL = os.getenv('GRAPH_SERVICE_URL', 'http://graph-service:5004')
PREDICTION_API_URL = os.getenv('PREDICTION_API_URL', 'http://localhost:5001/predict')

# Buffer to retain recent prediction events for building a lightweight graph snapshot
recent_events = []  # each item: {id, amount, prediction_score, recommendation, ts}
MAX_EVENTS = 200


def _call_prediction_api(features):
    """Helper to call the prediction API with graceful fallback."""
    prediction_score = None
    try:
        resp = requests.post(PREDICTION_API_URL, json={'features': features}, timeout=2)
        if resp.ok:
            prediction_score = float(resp.json().get('score', 0.5))
    except Exception:
        prediction_score = None
    if prediction_score is None:
        # Fallback heuristic if the prediction API is unavailable
        prediction_score = sum(features) / len(features) if features else 0.5
    return prediction_score

@app.route('/api/users/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_service_proxy(path):
    response = requests.request(
        method=request.method,
        url=f'{USER_SERVICE_URL}/api/users/{path}',
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    return (response.content, response.status_code, response.headers.items())

@app.route('/api/transactions/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def transaction_service_proxy(path):
    response = requests.request(
        method=request.method,
        url=f'{TRANSACTION_SERVICE_URL}/api/transactions/{path}',
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)
    return (response.content, response.status_code, response.headers.items())

# Similar routes for other services...

@app.route('/fraud/stream')
def fraud_stream():
    def event_gen():
        while True:
            amount = round(random.uniform(5, 1500), 2)
            base_features = [amount / 2000, random.random(), random.random()]
            prediction_score = _call_prediction_api(base_features)

            # Build a transaction-like payload and run it through the
            # prevention decision engine so the stream reflects real
            # approve / review / decline logic.
            tx_id = f"tx_{random.randint(100000, 999999)}"
            tx_payload = {
                'id': tx_id,
                'user_id': f'user_{random.randint(1, 50)}',
                'amount': amount,
                'risk_score': prediction_score,
            }
            decision_result = evaluate_transaction(tx_payload)

            # Map decision into the existing recommendation field used
            # by the dashboard. We keep title case labels for display.
            decision_label_map = {
                'DECLINE': 'Reject',
                'REVIEW': 'Review',
                'APPROVE': 'Approve',
            }
            recommendation = decision_label_map.get(decision_result.decision, 'Review')

            evt = {
                'id': tx_id,
                'amount': amount,
                'prediction_score': round(prediction_score, 4),
                'risk_score': round(prediction_score, 4),
                'recommendation': recommendation,
                'risk_category': decision_result.risk_category,
                'decision': decision_result.decision,
                'rules': decision_result.reasons,
                'features': base_features,
                'time': int(time.time())
            }
            recent_events.append(evt)
            if len(recent_events) > MAX_EVENTS:
                del recent_events[0:len(recent_events)-MAX_EVENTS]
            yield f"data: {json.dumps(evt)}\n\n"
            time.sleep(1.0)

    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
    }
    return Response(stream_with_context(event_gen()), headers=headers)

@app.route('/fraud/transactions')
def fraud_transactions():
    """Return a snapshot of recent transactions for the overview table.

    Instead of generating synthetic rows independently from the live
    stream, we now surface the same recent_events buffer used by the
    dashboard so that history is consistent across pages.
    """

    window = list(recent_events)[-50:]
    if not window:
        # Fallback to a small synthetic sample if no events exist yet
        items = []
        for _ in range(25):
            amount = round(random.uniform(5, 2000), 2)
            base_features = [amount / 2000, random.random(), random.random()]
            score = _call_prediction_api(base_features)
            tx_id = f"tx_{random.randint(100000, 999999)}"
            decision = evaluate_transaction({
                'id': tx_id,
                'user_id': f'user_{random.randint(1, 50)}',
                'amount': amount,
                'risk_score': score,
            })
            items.append({
                'id': tx_id,
                'amount': amount,
                'score': round(score, 4),
                'decision': decision.decision,
                'risk_category': decision.risk_category,
            })
        return jsonify(items)

    items = []
    for e in window:
        items.append({
            'id': e.get('id'),
            'amount': e.get('amount', 0.0),
            'score': round(float(e.get('prediction_score', 0.0)), 4),
            'decision': e.get('decision'),
            'risk_category': e.get('risk_category'),
        })
    return jsonify(items)

@app.route('/graph/network')
def graph_network():
    # Derive a simple graph from recent events by grouping transactions into pseudo communities
    events_snapshot = list(recent_events)[-50:]
    if not events_snapshot:
        # Fallback random graph
        nodes = [
            {'id': i, 'risk': round(random.random(), 4), 'connections': 0}
            for i in range(15)
        ]
        links = []
        for i in range(len(nodes)):
            for _ in range(random.randint(1, 3)):
                tgt = random.randint(0, len(nodes)-1)
                if tgt != i:
                    links.append({'source': i, 'target': tgt})
                    nodes[i]['connections'] += 1
                    nodes[tgt]['connections'] += 1
        return jsonify({'nodes': nodes, 'links': links})
    # Build nodes: last N events become nodes
    nodes = []
    links = []
    # Simple community assignment by recommendation category
    category_groups = {}
    for e in events_snapshot:
        cat = e['recommendation']
        category_groups.setdefault(cat, []).append(e)
    # Assign node ids
    idx = 0
    node_map = {}
    for cat, evs in category_groups.items():
        for ev in evs:
            risk = ev['prediction_score']
            node = {
                'id': idx,
                'tx_id': ev['id'],
                'risk': risk,
                'amount': ev['amount'],
                'category': cat,
                'connections': 0
            }
            nodes.append(node)
            node_map[ev['id']] = idx
            idx += 1
    # Link nodes within same category window
    for cat, evs in category_groups.items():
        ids = [node_map[e['id']] for e in evs]
        for i in range(len(ids)):
            for j in range(i+1, min(i+1+3, len(ids))):  # limit density
                links.append({'source': ids[i], 'target': ids[j]})
                nodes[ids[i]]['connections'] += 1
                nodes[ids[j]]['connections'] += 1
    return jsonify({'nodes': nodes, 'links': links})

@app.route('/analytics/heatmap')
def analytics_heatmap():
    # Build 7 (Mon-Sun) x 12 (2-hour blocks) matrix from recent events
    days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    # Initialize structure
    grid = {d: [{'count': 0, 'sum_risk': 0.0} for _ in range(12)] for d in days_order}
    for e in recent_events:
        ts = e.get('time')
        if not ts: continue
        dt = time.gmtime(ts)
        weekday = days_order[dt.tm_wday]
        hour_block = dt.tm_hour // 2  # 0..11
        if hour_block > 11: hour_block = 11
        cell = grid[weekday][hour_block]
        cell['count'] += 1
        cell['sum_risk'] += e.get('risk_score', 0.0)
    # Build response
    response = []
    for d in days_order:
        slots = []
        for i, cell in enumerate(grid[d]):
            count = cell['count']
            avg = (cell['sum_risk'] / count) if count > 0 else 0.0
            slots.append({
                'hour_block': i,
                'start': f"{i*2:02d}:00",
                'count': count,
                'avg_risk': round(avg, 4)
            })
        response.append({'day': d, 'slots': slots})
    return jsonify(response)

@app.route('/events/explain/<tx_id>')
def events_explain(tx_id):
    # Find event
    target = None
    for e in reversed(recent_events):
        if e['id'] == tx_id:
            target = e
            break
    if not target:
        return jsonify({'error': 'transaction not found'}), 404
    # Call prediction API explanation endpoint
    try:
        resp = requests.post(PREDICTION_API_URL.replace('/predict','/explain'), json={
            'features': target.get('features', []),
            'graph_context': {'neighbors': [], 'community': target.get('risk_category')}
        }, timeout=3)
        if resp.ok:
            data = resp.json()
            return jsonify({'tx_id': tx_id, 'explanation': data, 'risk_score': target.get('risk_score')})
    except Exception as ex:
        return jsonify({'error': 'explain call failed', 'detail': str(ex)}), 502
    return jsonify({'error': 'explain unavailable'}), 503

@app.route('/metrics')
def metrics():
    window = list(recent_events)
    total = len(window)
    if total == 0:
        return jsonify({'total_events': 0})
    avg_score = sum(e['prediction_score'] for e in window) / total
    high = sum(1 for e in window if e['prediction_score'] > 0.85)
    medium = sum(1 for e in window if 0.6 < e['prediction_score'] <= 0.85)
    low = sum(1 for e in window if e['prediction_score'] <= 0.6)
    return jsonify({
        'total_events': total,
        'avg_prediction_score': round(avg_score, 4),
        'distribution': {'high': high, 'medium': medium, 'low': low},
        'timestamp': int(time.time())
    })

@app.route('/events/recent')
def events_recent():
    # Return last 50 events
    return jsonify(list(recent_events)[-50:])


@app.route('/decision/authorize', methods=['POST'])
def decision_authorize():
    """Synchronous decision endpoint for transaction authorization.

    Expected JSON body (all optional except amount for realistic use):
      - transaction_id
      - user_id
      - amount
      - features: list of numeric features for the model

    The endpoint calls the prediction API to obtain a risk score,
    then runs the prevention decision engine and returns a structured
    decision payload that calling systems can use to APPROVE, REVIEW,
    or DECLINE a transaction.
    """

    payload = request.get_json(force=True) or {}
    amount = payload.get('amount', 0.0)
    tx_id = payload.get('transaction_id') or f"tx_{random.randint(100000, 999999)}"
    user_id = payload.get('user_id', None)
    features = payload.get('features')
    if not isinstance(features, list):
        # Simple default feature construction if none are provided
        try:
            amt = float(amount)
        except Exception:
            amt = 0.0
        features = [amt / 2000.0, random.random(), random.random()]

    score = _call_prediction_api(features)
    tx_payload = {
        'id': tx_id,
        'user_id': user_id,
        'amount': amount,
        'risk_score': score,
    }
    decision_result = evaluate_transaction(tx_payload)

    # Best-effort audit logging of the decision with a simple hash
    decision_dict = decision_result.to_dict()
    audit_payload = {
        'transaction': decision_dict,
        'features': features,
    }
    try:
        serialized = json.dumps(audit_payload, sort_keys=True).encode('utf-8')
        audit_payload['hash'] = hashlib.sha256(serialized).hexdigest()
    except Exception:
        audit_payload['hash'] = None
    log_explanation(audit_payload)

    # Also push the event into the in-memory buffer so the dashboard
    # reflects decisions made through this endpoint.
    evt = {
        'id': decision_result.transaction_id,
        'amount': decision_result.amount,
        'prediction_score': round(decision_result.risk_score, 4),
        'risk_score': round(decision_result.risk_score, 4),
        'recommendation': {
            'DECLINE': 'Reject',
            'REVIEW': 'Review',
            'APPROVE': 'Approve',
        }.get(decision_result.decision, 'Review'),
        'risk_category': decision_result.risk_category,
        'decision': decision_result.decision,
        'rules': decision_result.reasons,
        'features': features,
        'time': int(time.time()),
    }
    recent_events.append(evt)
    if len(recent_events) > MAX_EVENTS:
        del recent_events[0:len(recent_events)-MAX_EVENTS]

    return jsonify({
        'transaction_id': decision_result.transaction_id,
        'user_id': decision_result.user_id,
        'amount': decision_result.amount,
        'risk_score': decision_result.risk_score,
        'risk_category': decision_result.risk_category,
        'decision': decision_result.decision,
        'reasons': decision_result.reasons,
        'actions': decision_result.actions,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)