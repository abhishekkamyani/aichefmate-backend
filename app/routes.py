from flask import Blueprint, jsonify, request
from .auth import jwt_required
import requests
import base64
import os
import re
import json

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

@bp.route('/identify-ingredients', methods=['POST'])
# @jwt_required
def generate_content():
    data = request.json
    image_data = data.get('image')  # Base64 encoded image
    # text_input = "Identify all the ingredients in the image with high accuracy and return only the result in the following format: { 'ingredients': ['ingredient1', 'ingredient2', 'ingredient3']} Do not include any explanation or extra text. must be simple text format"
    text_input = "Identify only raw, uncooked food ingredients present in the image, such as fruits, vegetables, grains, spices, or similar. Ignore any background elements (like trees, sky, birds) and cooked foods or meals. If no raw ingredients are detected, return an empty list. Respond only in the following JSON format without any explanation or extra text: { 'ingredients': ['ingredient1', 'ingredient2', 'ingredient3' }"
    payload = {
        "contents": [{
            "parts": []
        }]
    }

    payload["contents"][0]["parts"].append({"text": text_input})

    if image_data:
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        payload["contents"][0]["parts"].append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        })

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        # Extract ingredients list from the model response
        raw_text = data['candidates'][0]['content']['parts'][0]['text']

        # Remove ```json and ``` if present
        clean_text = re.sub(r"```json|```", "", raw_text).strip()

        # Convert to Python dict
        ingredients_json = json.loads(clean_text.replace("'", '"'))  # replace single quotes with double quotes

        return jsonify(ingredients_json)

    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
        return jsonify({"error": str(e)}), 500