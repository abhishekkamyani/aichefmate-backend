from functools import wraps
from flask import request, jsonify
from utils.supabase import supabase
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(error="Missing token"), 401

        token = auth_header.split(" ")[1]
        # logger.info(f"Verifying token: {token[:15]}...")

        try:
            # Verify token using Supabase client
            user = supabase.auth.get_user(token)
            request.user = user
            # logger.info(f"Authenticated user: {user.user.email}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            # logger.error(f"Authentication failed: {str(e)}")
            return jsonify(error="Invalid token"), 401

    return decorated