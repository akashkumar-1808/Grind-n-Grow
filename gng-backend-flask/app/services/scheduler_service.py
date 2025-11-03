from ..models import User, Subject, Session
from ..extensions import db
from ..utils import start_of_week
from datetime import timedelta, datetime
import math

FOCUS_CONFIG = {
    "SPRINTER": {"session_min": 25, "break_min": 5, "sessions_per_subject_limit": 2},
    "BALANCER": {"session_min": 45, "break_min": 10, "sessions_per_subject_limit": 1},
    "DEEP_DIVER": {"session_min": 60, "break_min": 15, "sessions_per_subject_limit": 1}
}

def focus_config_value(focus_type):
    if not focus_type:
        return FOCUS_CONFIG["BALANCER"]
    return FOCUS_CONFIG.get(focus_type.value, FOCUS_CONFIG["BALANCER"])

def generate_weekly_schedule(user_id: str, week_start_date: datetime):
    # ensure week_start is normalized to day boundary (Monday)
    week_start = start_of_week(week_start_date)
    week_end = week_start + timedelta(days=7)

    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    cfg = focus_config_value(user.focus_type)
    preferred_hours = (user.preferences or {}).get("preferredDailyHours", 2)

    # load subjects and compute remaining units
    subjects = []
    for s in user.subjects:
        remaining = max(0, (s.total_units or 0) - (s.units_done or 0))
        subjects.append({
            "db": s,
            "remaining": remaining,
            "exam_date": s.exam_date
        })

    # priority sort: earliest exam_date first; no exam -> sort by remaining desc
    def cmp_key(x):
        return (x["exam_date"] or datetime.max, -x["remaining"])
    subjects.sort(key=cmp_key)

    # idempotency: delete existing sessions for the week
    Session.query.filter(Session.user_id == user_id, Session.start >= week_start, Session.start < week_end).delete()
    db.session.commit()

    sessions_created = []
    # For each day allocate sessions until preferred hours reached
    for d in range(7):
        day_start = week_start + timedelta(days=d)
        allocated_minutes = 0
        # schedule start day at 9am base
        base_start = datetime(day_start.year, day_start.month, day_start.day, 9, 0)
        for subj in subjects:
            if subj["remaining"] <= 0:
                continue
            if allocated_minutes >= preferred_hours * 60:
                break
            # apply escalation if exam in < 7 days
            incr_sessions_allowed = 0
            if subj["exam_date"]:
                days_to_exam = (subj["exam_date"].date() - day_start.date()).days
                if days_to_exam <= 7:
                    incr_sessions_allowed = cfg["sessions_per_subject_limit"]  # allow more if close

            duration = cfg["session_min"]
            start_dt = base_start + timedelta(minutes=allocated_minutes)
            end_dt = start_dt + timedelta(minutes=duration)
            # create session
            s = Session(user_id=user_id, subject_id=subj["db"].id, start=start_dt, end=end_dt, duration_min=duration)
            db.session.add(s)
            sessions_created.append(s)
            db.session.flush()
            allocated_minutes += duration + cfg["break_min"]
            subj["remaining"] -= 1

    db.session.commit()
    return {"sessionsCreated": len(sessions_created), "sessions": [ {"id": s.id, "subjectId": s.subject_id, "start": s.start.isoformat(), "end": s.end.isoformat()} for s in sessions_created ]}
