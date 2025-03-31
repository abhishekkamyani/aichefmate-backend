from flask import Flask
from dotenv import load_dotenv
import os
from flask_cors import CORS


load_dotenv()  # Load before creating app

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')  # From .env
    
    # Proper CORS configuration
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Authorization", "Content-Type"],
            "supports_credentials": True
        }
    })

    from .routes import bp
    app.register_blueprint(bp)

    return app