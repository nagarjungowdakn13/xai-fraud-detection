from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import pymongo
import os
import json
from kafka import KafkaProducer

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
db = client['fraud_detection']
transactions_collection = db['transactions']

# Kafka producer
kafka_producer = KafkaProducer(
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

ML_SERVICE_URL = os.getenv('ML_SERVICE_URL', 'http://ml-service:5003')

@app.route('/api/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    current_user = get_jwt_identity()
    data = request.get_json()
    transaction = {
        'user_email': current_user['email'],
        'amount': data['amount'],
        'merchant': data['merchant'],
        'location': data.get('location'),
        'timestamp': data.get('timestamp')
    }
    
    # Send transaction to Kafka for real-time processing
    kafka_producer.send('transactions', value=transaction)
    
    # Also store in MongoDB
    transactions_collection.insert_one(transaction)
    
    # Get fraud prediction from ML service
    ml_response = requests.post(f'{ML_SERVICE_URL}/api/predict', json=transaction)
    fraud_prediction = ml_response.json()
    
    return jsonify({
        'transaction_id': str(transaction['_id']),
        'fraud_prediction': fraud_prediction
    }), 201

@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user = get_jwt_identity()
    transactions = list(transactions_collection.find({'user_email': current_user['email']}, {'_id': 0}))
    return jsonify(transactions), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)