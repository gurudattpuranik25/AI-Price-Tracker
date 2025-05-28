from flask import Blueprint, request, jsonify
from bson.objectid  import ObjectId
from app import mongo
import jwt
import os
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.background_price_checker import get_price

product_bp = Blueprint("products", __name__)

# Middleware to verify JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"_id": ObjectId(data["user_id"])})
            if not current_user:
                return jsonify({"error": "User not found"}), 401
        except Exception as e:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(current_user, *args, **kwargs)
    return decorated

# 📌 Add product
@product_bp.route("/add", methods=["POST"])
@token_required
def add_product(current_user):
    data = request.json
    url = data.get("url")
    target_price = data.get("target_price")
    phone_number = data.get("phone_number")

    if not url or not target_price or not phone_number:
        return jsonify({"error": "Missing fields"}), 400

    title, current_price = get_price(url)
    # print(f"Fetched title: {title}, current price: {current_price} for URL: {url}")
       
    mongo.db.products.insert_one({
        "user_id": current_user["_id"],
        "url": url,
        "target_price": target_price,
        "title": title,
        "current_price": current_price,
        "phone_number": phone_number
    })

    return jsonify({"message": "Product added successfully"}), 201

# 📌 Get all products
@product_bp.route("/all", methods=["GET"])
@token_required
def get_products(current_user):
    products = list(mongo.db.products.find({"user_id": current_user["_id"]}))
    for p in products:
        p["_id"] = str(p["_id"])
        p["user_id"] = str(p["user_id"])
    return jsonify(products)

@product_bp.route("/<product_id>", methods=["DELETE"])
#@jwt_required()
def delete_product(product_id):
    #user_id = get_jwt_identity()
    # Optional: Verify ownership
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    # if str(product["user_id"]) != user_id:
    #     return jsonify({"error": "Unauthorized"}), 403

    mongo.db.products.delete_one({"_id": ObjectId(product_id)})

    return jsonify({"message": "Product deleted successfully"}), 200

@product_bp.route("/<product_id>", methods=["PUT"])
#@jwt_required()
def update_product(product_id):
    data = request.json
    #user_id = get_jwt_identity()

    # Optional: Verify ownership of product (recommended)
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    # if str(product["user_id"]) != user_id:
    #     return jsonify({"error": "Unauthorized"}), 403

    update_fields = {
        "url": data.get("url"),
        "target_price": data.get("target_price"),
        "phone_number": data.get("phone_number")
    }

    mongo.db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_fields}
    )

    return jsonify({"message": "Product updated successfully"}), 200