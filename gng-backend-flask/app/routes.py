from flask import Blueprint, request, jsonify
from .extensions import db
from .models import User  # Assuming you have a User model defined in models.py

routes = Blueprint("routes", __name__)

@routes.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Save to DB (simple example)
    new_user = User(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Signup successful!"}), 201


def register_routes(app):
    app.register_blueprint(routes)
