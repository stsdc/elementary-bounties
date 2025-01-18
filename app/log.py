"""Logging module.
Origin: https://github.com/JakubPluta/gymhero/blob/main/gymhero/log.py"""

import logging
import sys
from typing import Optional
from typing import Any, Dict
from uvicorn.logging import ColourizedFormatter
from uvicorn.config import LOGGING_CONFIG


LOGGING_FORMATTER = "%(levelprefix)s [%(asctime)s] [%(name)s] %(message)s"
DATE_FMT = "%d-%m-%Y %H:%M:%S"


def timestamp_log_config() -> Dict[str, Any]:
    """
    Configures and returns the logging configuration dictionary with updated formatters.

    This function modifies the 'default' and 'access' formatters in the global LOGGING_CONFIG
    dictionary to include specific formatting strings and date formats.

    Returns:
        Dict[str, Any]: The updated logging configuration dictionary.
    """

    formatters = LOGGING_CONFIG["formatters"]
    formatters["default"]["fmt"] = LOGGING_FORMATTER
    formatters["access"][
        "fmt"
    ] = '%(levelprefix)s [%(asctime)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
    formatters["access"]["datefmt"] = DATE_FMT
    formatters["default"]["datefmt"] = DATE_FMT
    return LOGGING_CONFIG


DebugLevels = ["DEBUG", "INFO", "WARNING", "ERROR"]
DebugLevelType = str


def get_logger(
    name: Optional[str] = None, level: DebugLevelType = "DEBUG"
) -> logging.Logger:
    """
    Creates and configures a logger for logging messages.

    Parameters:
        name (Optional[str]): The name of the logger. Defaults to None.
        level (DebugLevel): The logging level. Defaults to DebugLevel.DEBUG.

    Returns:
        logging.Logger: The configured logger object.
    """
    logger = logging.getLogger(name=name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = ColourizedFormatter(fmt=LOGGING_FORMATTER, datefmt=DATE_FMT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if not level or level not in DebugLevels:
        logger.warning(
            "Invalid logging level %s. Setting logging level to DEBUG.", level
        )
        level = "DEBUG"

    logger.setLevel(level=level)
    return logger
