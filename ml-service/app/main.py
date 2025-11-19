from flask import Flask, request, jsonify
import pandas as pd
import joblib
import os
from model import AdaptiveFraudDetector  # Assume we have a model class

app = Flask(__name__)

# Load model
model = AdaptiveFraudDetector()
model.load(os.getenv('MODEL_PATH', '/app/models/'))

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # Preprocess the data
    features = preprocess(data)
    # Predict
    prediction = model.predict(features)
    explanation = model.explain(features)
    return jsonify({
        'fraud_probability': prediction,
        'explanation': explanation
    })

@app.route('/api/train', methods=['POST'])
def train():
    # Endpoint to retrain the model with new data
    data = request.get_json()
    model.train(data)
    return jsonify({'message': 'Model trained successfully'})

def preprocess(data):
    # Preprocess the incoming data to features
    # This is a simplified example
    features = [
        data['amount'],
        # ... other features
    ]
    return [features]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)