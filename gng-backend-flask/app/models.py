from .extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import enum
import uuid

def gen_id():
    return str(uuid.uuid4())

class FocusType(enum.Enum):
    SPRINTER = "SPRINTER"
    BALANCER = "BALANCER"
    DEEP_DIVER = "DEEP_DIVER"

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String, primary_key=True, default=gen_id)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=True)
    focus_type = db.Column(db.Enum(FocusType), default=FocusType.BALANCER)
    preferences = db.Column(JSONB, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subjects = db.relationship("Subject", backref="user", cascade="all, delete-orphan")
    sessions = db.relationship("Session", backref="user", cascade="all, delete-orphan")
    refresh_tokens = db.relationship("RefreshToken", backref="user", cascade="all, delete-orphan")

class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.String, primary_key=True, default=gen_id)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String, nullable=False)
    total_units = db.Column(db.Integer, nullable=False, default=0)
    units_done = db.Column(db.Integer, nullable=False, default=0)
    exam_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sessions = db.relationship("Session", backref="subject", cascade="all, delete-orphan")

class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.String, primary_key=True, default=gen_id)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    subject_id = db.Column(db.String, db.ForeignKey("subjects.id"), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeeklyGoal(db.Model):
    __tablename__ = "weekly_goals"
    id = db.Column(db.String, primary_key=True, default=gen_id)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    week_start = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String, nullable=False)
    target_units = db.Column(db.Integer, nullable=False)
    completed_units = db.Column(db.Integer, default=0)

class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"
    id = db.Column(db.String, primary_key=True, default=gen_id)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String, unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
