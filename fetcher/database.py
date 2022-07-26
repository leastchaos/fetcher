"""redis helper functions"""
import os

import redis
import ujson

# get a url that points to the redis server in the same folder as file
FILENAME = "fetcher.sock"
SEPERATOR = "::"


def get_url():
    """search for the url to the redis server"""
    for root, dirs, files in os.walk(os.path.dirname(os.getcwd())):
        for file in files:
            if file == FILENAME:
                return "unix:///" + os.path.join(root, file)
    return None


URL = get_url()
print(URL)

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
