"""Logging configuration for peakbagger-cli using loguru."""

import sys

from loguru import logger


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

    # Determine log level and format
    if debug:
        level = "DEBUG"
        # Debug mode: include file and line number for detailed debugging
        log_format = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{file}:{line}</cyan> - <level>{message}</level>"
    elif verbose:
        level = "INFO"
        # Verbose mode: clean format without file/line info
        log_format = (
            "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        )
    else:
        # Disable logging by setting level very high
        level = "CRITICAL"
        log_format = (
            "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        )

    # Add stderr handler with appropriate level and format
    logger.add(
        sys.stderr,
        level=level,
        format=log_format,
        colorize=True,
        backtrace=debug,
        diagnose=debug,
    )


# Create a logger instance for use throughout the application
def get_logger():
    """Get the configured logger instance."""
    return logger
