from datetime import datetime, timedelta
from pathlib import Path

from .storage import read_json, write_json


class RateLimiter:
    def __init__(self, path: Path, max_per_day: int) -> None:
        self.path = path
        self.max_per_day = max_per_day

    def can_upload(self, now: datetime) -> bool:
        data = read_json(self.path, {"date": None, "count": 0})
        if data["date"] != now.strftime("%Y-%m-%d"):
            return True
        return data["count"] < self.max_per_day

    def record_upload(self, now: datetime) -> None:
        data = read_json(self.path, {"date": None, "count": 0})
        date_key = now.strftime("%Y-%m-%d")
        if data["date"] != date_key:
            data = {"date": date_key, "count": 0}
        data["count"] += 1
        write_json(self.path, data)

    def remaining(self, now: datetime) -> int:
        data = read_json(self.path, {"date": None, "count": 0})
        date_key = now.strftime("%Y-%m-%d")
        if data["date"] != date_key:
            return self.max_per_day
        return max(self.max_per_day - data["count"], 0)
