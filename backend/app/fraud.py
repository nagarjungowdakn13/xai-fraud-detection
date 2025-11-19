from flask import Blueprint, jsonify, Response, stream_with_context
import json
import time
import random

fraud_bp = Blueprint('fraud', __name__)

@fraud_bp.route('/transactions', methods=['GET'])
def get_transactions():
    # Mock data for frontend/pages/index.js
    # Generate random start index to ensure IDs look different on refresh
    start_id = random.randint(1000, 9000)
    # Randomize the number of transactions (between 8 and 15)
    count = random.randint(8, 15)
    
    transactions = [
        {
            "id": f"tx_{start_id + i}", 
            "amount": random.randint(10, 10000), 
            "score": random.random()
        }
        for i in range(count)
    ]
    return jsonify(transactions)

@fraud_bp.route('/stream')
def stream_fraud_alerts():
    # Mock SSE stream for frontend/pages/dashboard.js
    def generate():
        while True:
            data = {
                "id": f"tx_{random.randint(1000, 9999)}",
                "amount": random.randint(50, 5000),
                "risk_score": random.random(),
                "recommendation": random.choice(["Approve", "Reject", "Review"])
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(2)
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')
