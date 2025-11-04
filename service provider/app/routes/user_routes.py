from flask import Blueprint, request, jsonify, current_app
from ..schemas.user_schema import UserCreateSchema, UserUpdateSchema
from ..services.user_service import UserService
from marshmallow import ValidationError

user_bp = Blueprint("user_bp", __name__)
create_schema = UserCreateSchema()
update_schema = UserUpdateSchema()
service = UserService()

@user_bp.route("/", methods=["POST"])
def create_user():
    try:
        data = create_schema.load(request.json or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    try:
        user = service.create_user(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.exception("Error creating user")
        return jsonify({"error": "internal error"}), 500

    return jsonify({"user": user}), 201

@user_bp.route("/", methods=["GET"])
def list_users():
    users = service.list_users()
    return jsonify(users), 200

@user_bp.route("/<user_id>", methods=["GET"])
def get_user(user_id):
    u = service.get_user(user_id)
    if not u:
        return jsonify({"error": "not found"}), 404
    return jsonify(u), 200

@user_bp.route("/<user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        changes = update_schema.load(request.json or {})
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    updated = service.update_user(user_id, changes)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated), 200

@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    res = service.delete_user(user_id)
    if res.deleted_count == 0:
        return jsonify({"error": "not found"}), 404
    return jsonify({"message": "deleted"}), 200

@user_bp.route("/auth", methods=["POST"])
def auth():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    user = service.authenticate(email, password)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"user": user}), 200
