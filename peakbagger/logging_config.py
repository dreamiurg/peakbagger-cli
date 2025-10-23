"""Logging configuration for peakbagger-cli using loguru."""

import sys
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger


def configure_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure logging based on verbosity flags.

    By default, all logging is disabled. When verbose is True, INFO level logs
    are shown. When debug is True, both INFO and DEBUG level logs are shown with
    file and line information.

    Args:
        verbose: Enable INFO level logging (HTTP requests)
        debug: Enable DEBUG level logging (parsing details, rate limiting, etc.)
    """
    # Remove default handler
    logger.remove()

    # Only add handler if logging is enabled
    if debug:
        # Debug mode: include file and line number for detailed debugging
        logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{file}:{line}</cyan> - <level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    elif verbose:
        # Verbose mode: clean format without file/line info
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
            colorize=True,
            backtrace=False,
            diagnose=False,
        )
    # If neither verbose nor debug, no handler is added (logging disabled)


# Create a logger instance for use throughout the application
def get_logger() -> "Logger":
    """Get the configured logger instance."""
    return logger
