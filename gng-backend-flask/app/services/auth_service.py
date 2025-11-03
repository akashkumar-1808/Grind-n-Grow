from ..extensions import db
from ..models import User, RefreshToken, FocusType
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
import uuid

def register(name, email, password, preferred_daily_hours=None):
    existing = User.query.filter_by(email=email).first()
    if existing:
        raise ValueError("Email already in use")
    hashed = bcrypt.hash(password)
    prefs = {"preferredDailyHours": preferred_daily_hours} if preferred_daily_hours else None
    user = User(name=name, email=email, password=hashed, preferences=prefs, focus_type=FocusType.BALANCER)
    db.session.add(user)
    db.session.commit()
    access = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
    return {"user": {"id": user.id, "email": user.email, "name": user.name}, "accessToken": access}

def login(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.verify(password, user.password):
        raise ValueError("Invalid credentials")
    access = create_access_token(identity=user.id, expires_delta=timedelta(minutes=15))
    return {"user": {"id": user.id, "email": user.email, "name": user.name}, "accessToken": access}

def refresh_token_logic(refresh_token_str):
    # placeholder: implement persistent refresh tokens if needed
    return {"accessToken": create_access_token(identity="...")}
