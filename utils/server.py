import time
from datetime import datetime

from pymongo import MongoClient

from config import mongo_url

client = MongoClient(mongo_url)
db = client["MongoDB"]["MyCol"]


def _today():
    return time.mktime(datetime.utcnow().date().timetuple())


def log_percentage(json: dict) -> bool:
    recycling = json.get("recycling", 0)
    unrecyclable = json.get("unrecyclable", 0)
    compost = json.get("compost", 0)

    today = _today()

    result = db.find({"_id": today})

    if result is None:
        db.insert_one(
            {
                "_id": today,
                "recycling": recycling,
                "unrecyclable": unrecyclable,
                "compost": compost
            }
        )
    else:
        db.update_one(
            {
                "_id": today
            },
            {
                "$inc": {
                    "recycling": recycling,
                    "unrecyclable": unrecyclable,
                    "compost": compost
                }
            }
        )

log_percentage({"compost": 32})