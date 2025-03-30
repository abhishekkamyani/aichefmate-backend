from flask import Blueprint, jsonify
from .auth import jwt_required
from requests import request
bp = Blueprint("api", __name__)

@bp.route("/")
def home():
    return jsonify(message="Public endpoint")

@bp.route("/protected")
@jwt_required
def protected():
    return jsonify(
        message="Secure endpoint",
        user_id=request.user["sub"]  # From decoded JWT
    )