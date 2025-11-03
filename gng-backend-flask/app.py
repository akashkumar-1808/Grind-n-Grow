# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/gng_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret')

db = SQLAlchemy(app)

# ----------------- Models -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for future guest-claim
    title = db.Column(db.String(300), nullable=False)
    subject = db.Column(db.String(150), nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    study_hours = db.Column(db.Float, default=0)
    priority = db.Column(db.Integer, default=2)  # 1-high,2-medium,3-low
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- Utils -----------------
def task_to_dict(t: Task):
    return {
        "id": t.id,
        "title": t.title,
        "subject": t.subject,
        "deadline": t.deadline.isoformat() if t.deadline else None,
        "study_hours": t.study_hours,
        "priority": t.priority,
        "is_completed": t.is_completed,
        "created_at": t.created_at.isoformat()
    }

def session_to_dict(s: Session):
    return {
        "id": s.id,
        "task_id": s.task_id,
        "user_id": s.user_id,
        "start": s.start.isoformat(),
        "end": s.end.isoformat(),
        "duration_min": s.duration_min,
        "is_completed": s.is_completed
    }

# ----------------- Auth -----------------
@app.route('/')
def home():
    return jsonify({"message": "Backend is running successfully 🎉"})

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed = generate_password_hash(password)
    u = User(username=username, email=email, password=hashed)
    db.session.add(u)
    db.session.commit()
    return jsonify({"message": "Signup successful", "user": {"username": u.username, "email": u.email}}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid email or password"}), 401
    return jsonify({"message": "Login successful", "user": {"username": user.username, "email": user.email}}), 200

# ----------------- Task CRUD -----------------
# Add task (logged-in user)
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json() or {}
    user_email = data.get('user_email')
    title = data.get('title')
    if not user_email or not title:
        return jsonify({"error": "user_email and title required"}), 400

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    subject = data.get('subject')
    deadline = data.get('deadline')
    study_hours = float(data.get('study_hours', 0))
    priority = int(data.get('priority', 2))

    dt = None
    if deadline:
        try:
            dt = datetime.fromisoformat(deadline)
        except:
            try:
                dt = datetime.fromisoformat(deadline + "T00:00:00")
            except:
                dt = None

    t = Task(user_id=user.id, title=title, subject=subject, deadline=dt, study_hours=study_hours, priority=priority)
    db.session.add(t)
    db.session.commit()
    return jsonify({"task": task_to_dict(t)}), 201

# Get all tasks for a user (by email)
@app.route('/tasks/<string:email>', methods=['GET'])
def get_tasks(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"tasks": []}), 200
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.priority.asc(), Task.deadline.asc()).all()
    return jsonify({"tasks": [task_to_dict(t) for t in tasks]}), 200

# Update task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    t = Task.query.get(task_id)
    if not t:
        return jsonify({"error": "Task not found"}), 404
    data = request.get_json() or {}
    t.title = data.get('title', t.title)
    t.subject = data.get('subject', t.subject)
    if 'deadline' in data:
        try:
            t.deadline = datetime.fromisoformat(data.get('deadline')) if data.get('deadline') else None
        except:
            t.deadline = None
    if 'study_hours' in data:
        try:
            t.study_hours = float(data.get('study_hours', t.study_hours))
        except:
            pass
    if 'priority' in data:
        t.priority = int(data.get('priority', t.priority))
    if 'is_completed' in data:
        t.is_completed = bool(data.get('is_completed'))
    db.session.commit()
    return jsonify({"task": task_to_dict(t)}), 200

# Delete task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    t = Task.query.get(task_id)
    if not t:
        return jsonify({"error": "Task not found"}), 404
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

# ----------------- Sessions (scheduled slots) -----------------
@app.route('/sessions/<string:email>', methods=['GET'])
def get_sessions(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"sessions": []}), 200
    start_q = request.args.get('start')
    end_q = request.args.get('end')
    q = Session.query.filter_by(user_id=user.id)
    if start_q:
        try:
            sdt = datetime.fromisoformat(start_q)
            q = q.filter(Session.start >= sdt)
        except:
            pass
    if end_q:
        try:
            edt = datetime.fromisoformat(end_q)
            q = q.filter(Session.end <= edt)
        except:
            pass
    sessions = q.order_by(Session.start.asc()).all()
    return jsonify({"sessions": [session_to_dict(s) for s in sessions]}), 200

@app.route('/sessions', methods=['POST'])
def add_session():
    data = request.get_json() or {}
    user_email = data.get('user_email')
    start = data.get('start')
    end = data.get('end')
    duration_min = int(data.get('duration_min', 60))
    if not user_email or not start or not end:
        return jsonify({"error": "user_email, start and end required"}), 400
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    try:
        sdt = datetime.fromisoformat(start)
        edt = datetime.fromisoformat(end)
    except:
        return jsonify({"error": "Bad datetime format"}), 400
    sess = Session(user_id=user.id, start=sdt, end=edt, duration_min=duration_min)
    db.session.add(sess)
    db.session.commit()
    return jsonify({"session": session_to_dict(sess)}), 201

@app.route('/sessions/<int:session_id>', methods=['PATCH'])
def patch_session(session_id):
    s = Session.query.get(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    data = request.get_json() or {}
    if 'start' in data:
        try:
            s.start = datetime.fromisoformat(data.get('start'))
        except:
            pass
    if 'end' in data:
        try:
            s.end = datetime.fromisoformat(data.get('end'))
        except:
            pass
    if 'is_completed' in data:
        s.is_completed = bool(data.get('is_completed'))
    db.session.commit()
    return jsonify({"session": session_to_dict(s)}), 200

@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    s = Session.query.get(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    db.session.delete(s)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

# ----------------- Progress -----------------
@app.route('/progress/<string:email>', methods=['GET'])
def progress(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"dailyPercent": 0, "weeklyPercent": 0, "subjectProgress": []}), 200
    tasks = Task.query.filter_by(user_id=user.id).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.is_completed)
    weeklyPercent = int((completed / total) * 100) if total > 0 else 0
    subjects = {}
    for t in tasks:
        sub = t.subject or "Ungrouped"
        if sub not in subjects:
            subjects[sub] = {"total": 0, "done": 0}
        subjects[sub]["total"] += 1
        if t.is_completed:
            subjects[sub]["done"] += 1
    subjectProgress = [{"subject": k, "total": v["total"], "done": v["done"]} for k,v in subjects.items()]
    return jsonify({"dailyPercent": 0, "weeklyPercent": weeklyPercent, "subjectProgress": subjectProgress}), 200

# ----------------- Simple schedule generator -----------------
@app.route('/schedule/generate', methods=['POST'])
def generate_schedule():
    data = request.get_json() or {}
    user_email = data.get('user_email')
    week_start = data.get('week_start')
    if not user_email or not week_start:
        return jsonify({"error": "user_email and week_start required"}), 400
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    try:
        ws = datetime.fromisoformat(week_start)
    except:
        return jsonify({"error": "bad week_start format"}), 400
    week_end = ws + timedelta(days=7)
    # delete existing sessions in the week for user
    Session.query.filter(Session.user_id==user.id, Session.start >= ws, Session.start < week_end).delete()
    db.session.commit()
    # tasks with remaining hours
    tasks = Task.query.filter(Task.user_id==user.id, Task.study_hours > 0).order_by(Task.priority.asc(), Task.deadline.asc()).all()
    for t in tasks:
        t.remaining_minutes = int(t.study_hours * 60)
    created = []
    for day_offset in range(7):
        day = ws + timedelta(days=day_offset)
        current_min = 9 * 60
        while current_min + 60 <= 21 * 60:
            next_task = next((x for x in tasks if x.remaining_minutes > 0), None)
            if not next_task:
                break
            start_dt = datetime(day.year, day.month, day.day) + timedelta(minutes=current_min)
            end_dt = start_dt + timedelta(minutes=60)
            s = Session(user_id=user.id, task_id=next_task.id, start=start_dt, end=end_dt, duration_min=60)
            db.session.add(s)
            db.session.commit()
            created.append(session_to_dict(s))
            next_task.remaining_minutes -= 60
            current_min += 70
    return jsonify({"sessionsCreated": len(created), "sessions": created}), 201

# Create tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
