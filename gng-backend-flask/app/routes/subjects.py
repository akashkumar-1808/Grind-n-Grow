from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Subject, User
from ..extensions import db
from ..utils import parse_date

bp = Blueprint("subjects", __name__)

@bp.route("", methods=["POST"])
@jwt_required()
def create_subject():
    user_id = get_jwt_identity()
    body = request.get_json()
    s = Subject(user_id=user_id, name=body["name"], total_units=body.get("totalUnits", 0), exam_date=parse_date(body.get("examDate")))
    db.session.add(s)
    db.session.commit()
    return jsonify({"subject": {"id": s.id, "name": s.name}}), 201

@bp.route("", methods=["GET"])
@jwt_required()
def list_subjects():
    user_id = get_jwt_identity()
    subs = Subject.query.filter_by(user_id=user_id).all()
    out = []
    for s in subs:
        out.append({"id": s.id, "name": s.name, "totalUnits": s.total_units, "unitsDone": s.units_done, "examDate": s.exam_date.isoformat() if s.exam_date else None})
    return jsonify({"subjects": out})
