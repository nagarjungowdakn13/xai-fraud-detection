from flask import Blueprint, jsonify, request

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    return jsonify({"token": "mock-jwt-token", "user": {"id": 1, "username": "admin"}})

@auth_bp.route('/register', methods=['POST'])
def register():
    return jsonify({"message": "User registered successfully"})
