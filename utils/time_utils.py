import time
from datetime import datetime, timedelta


def get_today():
    return time.mktime(datetime.utcnow().date().timetuple())


def make_midnight(timestamp: int):
    return time.mktime(datetime.fromtimestamp(timestamp).date().timetuple())


def get_start_and_end_of_current_week():
    date_obj = datetime.utcnow().date()
    start_of_week = date_obj - timedelta(days=date_obj.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return time.mktime(start_of_week.timetuple()), time.mktime(end_of_week.timetuple())
