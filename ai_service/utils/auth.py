from functools import wraps
from flask import request, jsonify
import os

API_TOKEN = os.getenv("AI_SERVICE_TOKEN", "secret123")

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
