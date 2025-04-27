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
        r"/api/*": {
            "origins": [
                "http://localhost:8081",  # Expo web
                "exp://192.168.10.7:8081",  # Expo mobile
                "http://192.168.10.7:8081",  # Alternative Expo URL
                "http://192.168.10.7:5000", # Your Flask server
                "*"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "supports_credentials": True
        }
    })
    from .routes import bp
    app.register_blueprint(bp)

    return app