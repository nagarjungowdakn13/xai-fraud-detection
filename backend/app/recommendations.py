from flask import Blueprint, jsonify

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/<transaction_id>', methods=['GET'])
def get_recommendation(transaction_id):
    return jsonify({
        "transaction_id": transaction_id,
        "action": "Review",
        "reason": "High velocity of transactions"
    })
