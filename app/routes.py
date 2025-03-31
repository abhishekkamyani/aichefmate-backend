from flask import Blueprint, jsonify, request
from .auth import jwt_required

bp = Blueprint("api", __name__, url_prefix="/api")

@bp.route("/")
def api_root():
    """Main API endpoint"""
    return jsonify({
        "message": "API root endpoint",
        "endpoints": {
            "public": "/public",
            "protected": "/protected",
            "user_info": "/user"
        }
    })

@bp.route("/public")
def public():
    """Public endpoint (no auth required)"""
    return jsonify(message="Public endpoint")

@bp.route("/protected")
@jwt_required
def protected():
    """Protected endpoint (requires valid JWT)"""
    return jsonify(
        message="Secure endpoint - access granted",
        # user=request.user.user.dict()  # Now includes user details
    )

@bp.route("/user")
@jwt_required
def user_info():
    """Get detailed user info"""
    return jsonify(
        user=request.user.user.dict(),
        session=request.user.session.dict()
    )