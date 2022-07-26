"""set up logging"""
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler  # pylint: disable=unused-import

import coloredlogs


def setup_logging(
    name: str,
    log_level=logging.INFO,
    log_file_level=logging.INFO,
    log_filename="./logs/default.log",
) -> Logger:
    """Setup root logger and quiet some levels."""
    logger = logging.getLogger(name)

    # Set log format to dislay the logger name
    # and to hunt down verbose logging modules
    fmt = "%(asctime)s - %(name)-25s %(levelname)-8s %(message)s"

    # Use colored logging output for console
    coloredlogs.install(level=log_level, fmt=fmt, logger=logger)

    if log_filename:
        # Append to the log file
        handler = logging.handlers.RotatingFileHandler(
            log_filename, "a", maxBytes=500000, backupCount=2
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        handler.setLevel(log_file_level)
        logger.addHandler(handler)

    return logger
