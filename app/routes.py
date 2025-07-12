from flask import Blueprint, jsonify, request
from .auth import jwt_required
import requests
import base64
import os
import re
import json
import uuid
from utils.supabase import supabase # Import the single instance

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
    
    print("API Called")

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
    
# --- NEW ENDPOINT FOR RECIPE GENERATION ---
@bp.route('/generate-recipes', methods=['POST'])
@jwt_required
def generate_recipes_and_save():
    # """
    # Generates recipes, saves the original image and recipe data to Supabase,
    # and returns a lightweight summary of the recipes.
    # """
    data = request.json
    # print("===data===", data)
    ingredients = data.get('ingredients')
    image_base64 = data.get('image') # The original base64 image from the client
    user_id = request.user.id 
    
    print("===user_id===", user_id)

    if not all([ingredients, image_base64, user_id]):
        return jsonify({"error": "ingredients, image, and user_id are required."}), 400

    # --- Step 1: Generate recipes with Gemini API ---
    recipes_data = {}
    try:
        ingredients_str = ", ".join(ingredients)
        prompt = f"""
        Based on the following ingredients: {ingredients_str}.

        Generate exactly 5 creative and delicious recipes. Please provide the response as a single JSON object with a key "recipes" which contains a list of 5 recipe objects.

        Each recipe object must have the following structure and data types:
        - "id": a unique string.
        - "title": a string.
        - "imageUrl": a string (provide a URL for a relevant, high-quality, royalty-free image).
        - "description": a brief, enticing string description of the dish.
        - "rating": a float between 4.0 and 5.0.
        - "reviewCount": an integer.
        - "cookTime": a string (e.g., "30 mins").
        - "prepTime": a string (e.g., "15 mins").
        - "servings": a string (e.g., "4").
        - "difficulty": a string ("Easy", "Medium", or "Hard").
        - "ingredients": a list of objects, where each object has "quantity" (float or integer), "unit" (string), and "name" (string).
        - "instructions": a list of strings, where each string is a complete step in the cooking process from start to finish.

        Do not include any explanation, introductory text, or markdown formatting like ```json. Your response must be only the raw JSON object.
        """

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
            headers={'Content-Type': 'application/json'},
            json=payload
        )
        response.raise_for_status()
        gemini_response_data = response.json()
        raw_text = gemini_response_data['candidates'][0]['content']['parts'][0]['text']
        recipes_data = json.loads(re.sub(r"```json|```", "", raw_text).strip())
        
        if 'recipes' not in recipes_data or not recipes_data['recipes']:
             raise ValueError("No recipes were generated by the model.")

    except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, IndexError, ValueError) as e:
        print(f"Error during Gemini API call or data processing: {e}")
        return jsonify({"error": "Failed to generate recipes from the model.", "details": str(e)}), 500


    # --- Step 2: Upload original image to Supabase Storage ---
    image_url = None
    try:
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        image_bytes = base64.b64decode(image_base64)
        
        # CORRECTED PATH: Prepended 'private/' to match your RLS policy
        file_path = f"private/{user_id}/{uuid.uuid4()}.jpg"
        
        # Ensure your bucket is named 'ingredient_images' in Supabase
        supabase.storage.from_("ingredients").upload(file_path, image_bytes, {"content-type": "image/jpeg"})
        res = supabase.storage.from_("ingredients").get_public_url(file_path)
        image_url = res
        
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'message'):
             error_details = e.message
        print(f"Error uploading image to Supabase. Details: {error_details}")
        return jsonify({
            "error": "Failed to upload ingredient image.", 
            "details": f"This is likely a Row-Level Security (RLS) policy issue. Please check your policies. Raw error: {error_details}"
        }), 500
        
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'message'):
             error_details = e.message
        print(f"Error uploading image to Supabase. Details: {error_details}")
        return jsonify({
            "error": "Failed to upload ingredient image.", 
            "details": f"This is likely a Row-Level Security (RLS) policy issue. Please check your policies. Raw error: {error_details}"
        }), 500

    # --- Step 3: Save records to Supabase Database ---
    try:
        history_insert = {
            "user_id": user_id,
            "image_url": image_url,
            "source_ingredients": ingredients
        }
        history_response = supabase.table("generation_history").insert(history_insert).execute()
        generation_id = history_response.data[0]['id']

        recipes_to_insert = []
        for recipe in recipes_data['recipes']:
            recipes_to_insert.append({
                "id": str(uuid.uuid4()),
                "generation_id": generation_id,
                "title": recipe.get('title'),
                "image_url": recipe.get('imageUrl'),
                "description": recipe.get('description'),
                "cook_time": recipe.get('cookTime'),
                "difficulty": recipe.get('difficulty'),
                "full_recipe_data": recipe
            })
        supabase.table("recipes").insert(recipes_to_insert).execute()
        
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'message'):
             error_details = e.message
        print(f"Error saving data to Supabase DB. Details: {error_details}")
        return jsonify({
            "error": "Failed to save recipe history to the database.", 
            "details": f"This is likely a Row-Level Security (RLS) policy issue. Raw error: {error_details}"
        }), 500

    # --- Step 4: Return a lightweight summary to the client ---
    recipe_summary = [{
        "id": r.get("id"),
        "title": r.get("title"),
        "imageUrl": r.get("image_url"),
        "cookTime": r.get("cook_time"),
        "difficulty": r.get("difficulty")
    } for r in recipes_to_insert]

    return jsonify({"recipes": recipe_summary})


# --- NEW ENDPOINT: Get full recipe details by ID ---
@bp.route('/recipe/<recipe_id>', methods=['GET'])
# @jwt_required
def get_recipe_details(recipe_id):
    """Fetches the full details for a single recipe from the database."""
    try:
        response = supabase.table("recipes").select("full_recipe_data").eq("id", recipe_id).single().execute()

        if not response.data:
            return jsonify({"error": "Recipe not found."}), 404

        full_recipe = response.data.get('full_recipe_data')
        return jsonify(full_recipe)

    except Exception as e:
        print(f"Error fetching recipe details: {e}")
        return jsonify({"error": "Could not retrieve recipe details.", "details": str(e)}), 500

