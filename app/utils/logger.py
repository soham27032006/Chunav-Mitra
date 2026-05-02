"""
Module: logger.py
Purpose: Centralized structured logging factory for Chunav Mitra.
         All modules obtain their logger from this factory so format and
         output destination remain consistent across the application.
Author: Chunav Mitra Team
Version: 2.0.0
"""

from __future__ import annotations

import logging
import sys

__all__ = ["get_logger"]


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger instance for the given module.

    If the named logger already has handlers attached (e.g. when the same
    module is imported multiple times), the existing instance is returned
    without adding duplicate handlers.

    Args:
        name: Logger name, typically the calling module's ``__name__``.
        level: Logging level (default: ``logging.INFO``).

    Returns:
        Configured ``logging.Logger`` instance with a ``StreamHandler``
        writing structured output to ``stdout``.

    Raises:
        TypeError: When ``name`` is not a string.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Chunav Mitra started")
    """
    if not isinstance(name, str):
        raise TypeError(f"Logger name must be a string, got {type(name).__name__}")

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
