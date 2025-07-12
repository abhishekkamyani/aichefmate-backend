# In your auth.py file
from functools import wraps
from flask import request, jsonify
from utils.supabase import supabase # Make sure you are importing the shared client
from gotrue.errors import AuthApiError

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify(error="Missing or invalid Authorization header"), 401

        token = auth_header.split(" ")[1]

        try:
            # THIS IS THE CRITICAL STEP:
            # It authenticates the shared Supabase client for this specific request.
            supabase.auth.set_session(access_token=token, refresh_token=token)
            
            # Now, verify we have a valid user with the session we just set
            user_response = supabase.auth.get_user()
            if not user_response.user:
                 return jsonify(error="User for this token could not be found."), 401

            request.user = user_response.user
            
            # If authentication succeeds, execute the actual route function
            return f(*args, **kwargs)

        except AuthApiError as e:
            # This will catch specific Supabase auth errors (e.g., token expired)
            return jsonify(error="Supabase authentication error", details=e.message), 401
        except Exception as e:
            return jsonify(error="An unexpected server error occurred during authentication", details=str(e)), 500
        # finally:
        #     # VERY IMPORTANT: Always clear the session after the request is done.
        #     # This prevents the session from one user "leaking" to the next request on the server.
        #     supabase.auth.sign_out()
            
    return decorated