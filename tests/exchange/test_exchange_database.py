"""test fetcher database"""
import redis

from exchange.database import get_key, get_redis


def test_get_redis():
    """test get redis"""
    assert isinstance(get_redis(), redis.Redis)


def test_get_key():
    """test get key"""
    assert get_key("a", "b", "c") == "a::b::c"
