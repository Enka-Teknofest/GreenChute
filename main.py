import time
from datetime import datetime

from utils.config import mongo_url
from utils.mongomanager import MongoManager

db = MongoManager(mongo_url, "CopDetektor")


def log_percentage(type: str, percentage: int) -> bool:
    today = time.mktime(datetime.utcnow().date().timetuple())

    print(today)
    #result = db.db.find({"_id": today})
log_percentage("123", 123)