"""test fetcher database"""
import redis
from fetcher.database import get_redis, get_key

def test_get_redis():
    """test get redis"""
    assert isinstance(get_redis(), redis.Redis)


def test_get_key():
    """test get key"""
    assert get_key("a", "b", "c") == "a::b::c"
