from pymongo import MongoClient

import utils.time_utils as tu


class MongoConnection:

    def __init__(self, connect_url: str, database: str, collection: str):
        self.client = MongoClient(connect_url)
        self.db = self.client[database][collection]

    def log_percentage(self, json: dict):
        today = tu.get_today()
        result = self.db.find_one({"_id": today}, {"_id": 1})

        if result is None:
            self.db.insert_one({"_id": today, **json})
            return {"status": 1}
        else:
            self.db.update_one({"_id": today}, {"$inc": json})
            return {"status": 1}

    def get_todays_log(self):
        result = self.db.find_one({"_id": tu.get_today()}, {"_id": 0})
        if result is None:
            return {"status": 0}
        else:
            result.update({"status": 1})
            return result

    def get_weeks_log(self):
        start, end = tu.get_start_and_end_of_current_week()
        return self.db.find({"_id": {"$gte": start, "$lte": end}}).sort({"_id": -1})

    def get_from_gap(self, *, x: int, y: int, leap: int = 0):  # LEAP SOON
        times = [tu.make_midnight(x), tu.make_midnight(y)]
        times.sort()
        return self.db.find({"_id": {"$gte": times[0], "$lte": times[1]}}).sort({"_id": -1}).limit(10)

    @staticmethod
    def sum_up(to_sum: list):
        all_keys = set().union(*(d.keys() for d in to_sum))
        sum_dict = {}

        for d in to_sum:
            for key in all_keys:
                d.setdefault(key, 0)

        for key in all_keys:
            sum_dict[key] = float(sum(d[key] for d in to_sum)) / len(to_sum)

        return sum_dict
