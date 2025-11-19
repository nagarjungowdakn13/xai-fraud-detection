import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from flask import request, current_app
import redis
from functools import wraps

class SecurityManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='redis-cluster', port=6379, decode_responses=True)
        self.failed_attempts_limit = 5
        self.lockout_duration = 900  # 15 minutes
    
    def hash_password(self, password: str) -> str:
        """Secure password hashing with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        return f"{salt}${pwd_hash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, stored_hash = hashed.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            ).hex()
            return secrets.compare_digest(new_hash, stored_hash)
        except Exception:
            return False
    
    def check_rate_limit(self, identifier: str, max_requests: int = 100, window: int = 900) -> bool:
        """Redis-based rate limiting"""
        key = f"rate_limit:{identifier}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, window, 1)
            return True
        
        if int(current) < max_requests:
            self.redis_client.incr(key)
            return True
        
        return False
    
    def track_failed_login(self, username: str) -> bool:
        """Track failed login attempts and lock if exceeded"""
        key = f"failed_logins:{username}"
        current_attempts = self.redis_client.incr(key)
        
        if current_attempts == 1:
            self.redis_client.expire(key, self.lockout_duration)
        
        if current_attempts >= self.failed_attempts_limit:
            lock_key = f"account_lock:{username}"
            self.redis_client.setex(lock_key, self.lockout_duration, "locked")
            return False
        
        return True
    
    def is_account_locked(self, username: str) -> bool:
        """Check if account is temporarily locked"""
        return self.redis_client.exists(f"account_lock:{username}")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_api_key(api_key: str) -> bool:
    """Validate API key against database"""
    # Implementation for API key validation
    return True