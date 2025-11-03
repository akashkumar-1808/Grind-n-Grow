from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User, FocusType
from ..extensions import db

bp = Blueprint("focus", __name__)

# Example questions (frontend can use these)
QUESTIONS = [
    {"id": 1, "q": "Can you focus for long, uninterrupted periods?"},
    {"id": 2, "q": "Do you prefer short sprints of study?"},
    {"id": 3, "q": "Do you get bored on very long sessions?"}
]

@bp.route("/questions", methods=["GET"])
def questions():
    return jsonify({"questions": QUESTIONS})

@bp.route("/test/submit", methods=["POST"])
@jwt_required()
def submit_test():
    user_id = get_jwt_identity()
    body = request.get_json()
    answers = body.get("answers", [])
    # simple scoring: sum values
    score = sum(a.get("value", 0) for a in answers)
    # map to focusType
    if score <= 3:
        ft = FocusType.SPRINTER
    elif score <= 6:
        ft = FocusType.BALANCER
    else:
        ft = FocusType.DEEP_DIVER
    user = User.query.get(user_id)
    user.focus_type = ft
    db.session.commit()
    return jsonify({"focusType": ft.value})
