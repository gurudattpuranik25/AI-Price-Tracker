from flask import Flask
from extensions import mongo
from flask_cors import CORS
from dotenv import load_dotenv
import threading
import certifi
from flask_jwt_extended import JWTManager
import os


def create_app():
    load_dotenv()

    MONGO_URI = os.environ['MONGO_URI']

    app = Flask(__name__)
    # CORS(app, supports_credentials=True)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # Config
    app.config['MONGO_URI'] = MONGO_URI# JWT config

    mongo.init_app(app)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    from routes.product_routes import product_bp
    app.register_blueprint(product_bp, url_prefix="/api/products")
    from utils.background_price_checker import price_check_worker
    checker_thread = threading.Thread(target=price_check_worker, daemon=True)
    checker_thread.start()
    return app


if __name__ == "__main__":
    print("🚀 app.py started")
    app = create_app()
    app.run(host="0.0.0.0", port=8000)

    # app.run(debug=True, use_reloader=False)
