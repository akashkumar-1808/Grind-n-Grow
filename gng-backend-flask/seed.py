from app import create_app
from app.extensions import db
from app.models import User, Subject
from passlib.hash import bcrypt

def run_seed(app):
    with app.app_context():
        db.create_all()
        # avoid duplicates
        if User.query.filter_by(email="akash@test.com").first():
            print("Seed user exists")
            return
        hashed = bcrypt.hash("123456")
        user = User(name="Akash", email="akash@test.com", password=hashed)
        db.session.add(user)
        db.session.flush()
        s1 = Subject(user_id=user.id, name="Math", total_units=10, units_done=0)
        s2 = Subject(user_id=user.id, name="Physics", total_units=8, units_done=2)
        db.session.add_all([s1, s2])
        db.session.commit()
        print("Seed data created.")
