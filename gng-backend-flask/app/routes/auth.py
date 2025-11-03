from flask import Blueprint, request, jsonify
from ..services.auth_service import register, login
from ..extensions import db

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["POST"])
def route_register():
    data = request.get_json()
    try:
        res = register(data.get("name"), data.get("email"), data.get("password"), data.get("preferredDailyHours"))
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/login", methods=["POST"])
def route_login():
    data = request.get_json()
    try:
        res = login(data.get("email"), data.get("password"))
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
