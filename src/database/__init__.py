import json
from datetime import datetime

import redis

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_DB = 13

database = None


def start_database():
    global database
    database = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    if database.get("status") is None:
        database.set(
            "status",
            json.dumps({"start": int(datetime.utcnow().timestamp()), "n_requests": 0}),
        )


def get_database() -> redis.Redis:
    if database is None:
        start_database()
    return database


def get_status():
    return json.loads(get_database()["status"].decode("utf-8"))


def restart_status():
    get_database().delete("status")
    database.set(
        "status",
        json.dumps({"start": int(datetime.utcnow().timestamp()), "n_requests": 0}),
    )


def add_processed_request():
    status = get_status()
    status["n_requests"] += 1
    get_database().set("status", json.dumps(status))
