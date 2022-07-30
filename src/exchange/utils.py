"""set up logging"""
import asyncio
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import Awaitable, Callable

import async_timeout
import ccxt
import coloredlogs
import redis
from async_timeout import Any

from src.exchange.database import get_key, store_data

ListOfDict = list[dict[str, Any]]


def setup_logging(
    log_level=logging.INFO,
    log_file_level=logging.INFO,
    log_filename="./logs/default.log",
) -> Logger:
    """Setup root logger and quiet some levels."""
    logger = logging.getLogger()

    # Set log format to dislay the logger name
    # and to hunt down verbose logging modules
    fmt = "%(asctime)s - %(name)-25s %(levelname)-8s %(message)s"

    # Use colored logging output for console
    coloredlogs.install(level=log_level, fmt=fmt, logger=logger)
    logging.getLogger("asyncio").setLevel(logging.FATAL)
    logging.getLogger("ccxt.base.exchange").setLevel(logging.FATAL)

    if log_filename:
        # Append to the log file
        handler = RotatingFileHandler(log_filename, "a", maxBytes=500000, backupCount=2)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.setLevel(log_file_level)
        logger.addHandler(handler)

    return logger


async def safe_timeout_method(
    func: Callable[..., Awaitable[Any]],
    *args: Any,
    timeout: float = 30,
    fail_func: Callable[..., Awaitable[Any]] | None = None,
    fail_result: Any = None,
    fail_timeout: float = 30,
    log_str: str = None
) -> Any:
    """try calling the method, if failed return fail result"""
    try:
        async with async_timeout.timeout(timeout):
            result = await func(*args)
            return result
    except (ccxt.errors.NetworkError, asyncio.TimeoutError) as err:
        logging.getLogger(log_str).error(
            "%s(%s) failed: %s", func.__name__, args, err.__class__.__name__
        )
    if not fail_func:
        logging.getLogger(log_str).info(
            "%s(%s) failed, no fail func, returning fail result: %s",
            func.__name__,
            args,
            fail_result,
        )
        return fail_result
    return await safe_timeout_method(
        fail_func, *args, fail_result=fail_result, timeout=fail_timeout, log_str=log_str
    )


def safe_get_float(data: dict, key: str, default: float | None = None) -> float:
    """
    safe get float
    As ccxt values contains none in some cases, we need to check if it is None
    so we cannot directly use dict.get(key, default) method
    """
    value = data.get(key, default)
    if value:
        return float(value)
    return None


def safe_get_float_2(
    data: dict, key1: str, key2: str, default: float | None = None
) -> float:
    """safe get float for 2 keys"""
    value = data.get(key1, data.get(key2, default))
    if value:
        return float(value)
    return None


def safe_get_key_2(target: dict, key1: Any, key2: Any, default: Any = None) -> Any:
    """
    to get key 2 from dict if key 1 does not exist
    """
    return target.get(key1, target.get(key2, default))


def push_data(
    redis_client: redis.Redis,
    table: str,
    name: str,
    value: Any,
    expiry: float = 300,
) -> None:
    """helper function to push data to redis"""
    key = get_key(table, name)
    logging.info("push data to redis: %s", key)
    store_data(redis_client, key, value, expiry)
