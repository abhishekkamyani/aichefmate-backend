from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Load before creating app

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')  # From .env
    
    from .routes import bp
    app.register_blueprint(bp)

    return app