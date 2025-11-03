from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Session, Subject
from ..extensions import db
from ..utils import parse_date

bp = Blueprint("sessions", __name__)

@bp.route("/<session_id>", methods=["PATCH"])
@jwt_required()
def update_session(session_id):
    user_id = get_jwt_identity()
    s = Session.query.filter_by(id=session_id, user_id=user_id).first()
    if not s:
        return jsonify({"error": "Not found"}), 404
    body = request.get_json()
    if "start" in body:
        s.start = parse_date(body["start"])
    if "end" in body:
        s.end = parse_date(body["end"])
    if "isCompleted" in body:
        s.is_completed = bool(body["isCompleted"])
        if s.is_completed:
            subj = Subject.query.get(s.subject_id)
            if subj:
                subj.units_done += 1
    db.session.commit()
    return jsonify({"session": {"id": s.id, "isCompleted": s.is_completed}})

@bp.route("/<session_id>", methods=["DELETE"])
@jwt_required()
def delete_session(session_id):
    user_id = get_jwt_identity()
    deleted = Session.query.filter_by(id=session_id, user_id=user_id).delete()
    db.session.commit()
    return jsonify({"success": True})
