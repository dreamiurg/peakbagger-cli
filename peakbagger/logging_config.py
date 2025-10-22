"""Logging configuration for peakbagger-cli using loguru."""

import sys

from loguru import logger


def configure_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure logging based on verbosity flags.

    By default, all logging is disabled. When verbose is True, INFO level logs
    are shown. When debug is True, both INFO and DEBUG level logs are shown.

    Args:
        verbose: Enable INFO level logging (HTTP requests)
        debug: Enable DEBUG level logging (parsing details, rate limiting, etc.)
    """
    # Remove default handler
    logger.remove()

    # Determine log level
    if debug:
        level = "DEBUG"
    elif verbose:
        level = "INFO"
    else:
        # Disable logging by setting level very high
        level = "CRITICAL"

    # Add stderr handler with appropriate level
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
    )


# Create a logger instance for use throughout the application
def get_logger():
    """Get the configured logger instance."""
    return logger
