from flask import Blueprint, jsonify

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/visualize/<transaction_id>', methods=['GET'])
def visualize_graph(transaction_id):
    return jsonify({
        "nodes": [
            {"id": "user_1", "label": "User"},
            {"id": "card_1", "label": "Card"},
            {"id": "ip_1", "label": "IP"}
        ],
        "edges": [
            {"source": "user_1", "target": "card_1", "label": "OWNS"},
            {"source": "user_1", "target": "ip_1", "label": "USED"}
        ]
    })
