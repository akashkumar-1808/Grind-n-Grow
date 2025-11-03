from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..services.scheduler_service import generate_weekly_schedule
from datetime import datetime

bp = Blueprint("schedule", __name__)

@bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    scope = body.get("scope", "week")
    weekStart = datetime.utcnow()
    res = generate_weekly_schedule(user_id, weekStart)
    return jsonify(res)
