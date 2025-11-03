from flask import Flask, jsonify
from .extensions import db, migrate, jwt
from .routes import register_routes
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_routes(app)

    @app.get("/")
    def health():
        return jsonify({"status": "ok", "app": "GNG backend (Flask)"})

    return app
