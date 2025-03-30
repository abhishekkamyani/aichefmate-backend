import jwt
from jwt import PyJWKClient
from functools import wraps
from flask import request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Configure from .env
JWKS_URL = f"{os.getenv('SUPABASE_URL')}/auth/v1/jwks"
AUDIENCE = os.getenv('JWT_AUDIENCE')
ISSUER = os.getenv('JWT_ISSUER')

# Cache JWKS client
jwks_client = PyJWKClient(JWKS_URL, cache_keys=True, lifespan=3600)  # 1-hour cache

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(error="Missing token"), 401
        
        token = auth_header.split(" ")[1]

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=AUDIENCE,
                issuer=ISSUER
            )
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify(error="Token expired"), 401
        except Exception as e:
            return jsonify(error=f"Invalid token: {str(e)}"), 401

        return f(*args, **kwargs)
    return decorated