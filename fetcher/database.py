"""redis helper functions"""
import os

import redis
import ujson

# get a url that points to the redis server in the same folder as file
URL = f"unix:///{os.path.join(os.path.dirname(__file__), 'data', 'redis.sock')}"
SEPERATOR = "::"


def get_redis(url=URL) -> redis.Redis:
    """get redis client"""
    return redis.from_url(url=url)


def get_key(*args) -> str:
    """get key"""
    return SEPERATOR.join(args)


def deserialize(data: str | None) -> dict:
    """deserialize data"""
    if not data:
        return {}
    return ujson.loads(data)


def serialize(data: dict | str | None) -> str:
    """serialize data"""
    if not data:
        return ""
    return ujson.dumps(data)


def store_data(
    redis_client: redis.Redis, key: str, data: dict | str | None, expiry: float = 600
) -> None:
    """store data"""
    redis_client.set(key, serialize(data), expiry)


def get_data(redis_client: redis.Redis, key: str) -> dict:
    """get data"""
    return deserialize(redis_client.get(key))
