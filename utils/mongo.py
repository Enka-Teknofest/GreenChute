from typing import List

from pymongo import MongoClient

import utils.time_utils as t


class MongoConnection:

    def __init__(self, connect_url: str, database: str, collection: str) -> None:
        """Initializes the MongoConnection class.
        :param connect_url: The MongoDB url to connect to.
        :param database: The database to use.
        :param collection: The collection to use.
        """
        self.client = MongoClient(connect_url)
        self.db = self.client[database][collection]

    def log(self, json: dict) -> dict:
        """Logs a dict to the database, if the log already exists, it will be updated, otherwise it will be created, and the status will be 1.
        :param json: The key value pairs to log.
        :return: {'status': 1}
        """
        today = t.get_today()
        result = self.db.find_one({"_id": today}, {"_id": 1})
        if result is None:
            self.db.insert_one({"_id": today, **json})
            return {"status": 1}
        else:
            self.db.update_one({"_id": today}, {"$inc": json})
            return {"status": 1}

    def get_todays_log(self) -> dict:
        """Returns a dict of the current day's log, the status is 1 if the log exists, 0 otherwise.
        :return: A log dict.
        """
        result = self.db.find_one({"_id": t.get_today()}, {"_id": 0})
        if result is None:
            return {"status": 0}
        else:
            result.update({"status": 1})
            return result.sort("_id", -1)

    def get_weeks_logs(self) -> List[dict]:
        """Returns a list of dicts of the last 7 days' logs, will return an empty list if there are no logs.
        :return: List of log dicts.
        """
        start, end = t.get_start_and_end_of_current_week()
        return list(self.db.find({"_id": {"$gte": start, "$lte": end}}).sort("_id", -1))

    def get_from_gap(self, *, x: int, y: int, skip: int = 0) -> List[dict]:
        """Returns a list of first 10 logs dicts between the x timestamp and y timestamp, will return an empty list if there are no logs.
        :param x: The timestamp to start from or end at.
        :param y: The timestamp to start from or end at.
        :param skip: The number of logs to skip.
        :return: List of log dicts.
        """
        times = [t.make_midnight(x), t.make_midnight(y)]
        times.sort()
        return list(self.db.find({"_id": {"$gte": times[0], "$lte": times[1]}}).sort("_id", -1).skip(skip).limit(10))

    @staticmethod
    def sum_up(to_sum: list) -> dict:
        """Returns a dict of the sum of the values of the keys in the list.
        :param to_sum: The list of dicts to sum up.
        :return: A dict of the sum of the values of the keys in the list.
        """
        all_keys = set().union(*(d.keys() for d in to_sum))
        sum_dict = {}

        for d in to_sum:
            for key in all_keys:
                d.setdefault(key, 0)

        for key in all_keys:
            sum_dict[key] = float(sum(d[key] for d in to_sum)) / len(to_sum)

        return sum_dict
