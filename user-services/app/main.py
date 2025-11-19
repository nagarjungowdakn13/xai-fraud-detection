from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key')
jwt = JWTManager(app)

# MongoDB connection
client = pymongo.MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017'))
db = client['fraud_detection']
users_collection = db['users']

@app.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    user = {
        'email': data['email'],
        'password': hashed_password,
        'role': data.get('role', 'user')
    }
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 400
    users_collection.insert_one(user)
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/users/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users_collection.find_one({'email': data['email']})
    if user and check_password_hash(user['password'], data['password']):
        access_token = create_access_token(identity={'email': user['email'], 'role': user['role']})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/users/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()
    user = users_collection.find_one({'email': current_user['email']}, {'password': 0})
    return jsonify(user), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)