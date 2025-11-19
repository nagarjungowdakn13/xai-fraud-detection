from flask import Blueprint, jsonify

models_bp = Blueprint('models', __name__)

@models_bp.route('/status', methods=['GET'])
def model_status():
    return jsonify({"status": "active", "models_loaded": ["fraud_detector_v1", "isolation_forest"]})

@models_bp.route('/train', methods=['POST'])
def train_model():
    return jsonify({"message": "Training started", "job_id": "job_123"})
