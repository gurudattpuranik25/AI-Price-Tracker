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

    # Load environment variables
    MONGO_URI = os.environ.get("MONGO_URI")
    if not MONGO_URI:
        raise ValueError("❌ Missing environment variable: MONGO_URI")

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

    # Config
    app.config["MONGO_URI"] = MONGO_URI
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret")  # default fallback

    # Init extensions
    mongo.init_app(app)
    jwt = JWTManager(app)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from routes.product_routes import product_bp
    app.register_blueprint(product_bp, url_prefix="/api/products")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    # Background worker for price checks
    from utils.background_price_checker import price_check_worker
    checker_thread = threading.Thread(target=price_check_worker, daemon=True)
    checker_thread.start()

    return app


# Local development entrypoint
if __name__ == "__main__":
    print("🚀 Running Flask app in development mode")
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
