from datetime import datetime, timedelta
from dateutil import parser

def parse_date(s):
    if not s: 
        return None
    if isinstance(s, datetime):
        return s
    return parser.parse(s)

def start_of_week(date):
    # return Monday as start
    d = date - timedelta(days=date.weekday())
    return datetime(d.year, d.month, d.day)
