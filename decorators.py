# decorators.py
#
# Small collection of decorators used across the project.
# Currently provides: @safe  (wraps a function, logs exception, exits with code 1)

from __future__ import annotations

import logging
import sys
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def safe(func: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator for CLI entrypoints / top-level calls.
    If an exception happens:
      - logs a readable error message
      - exits with status code 1

    Use it on functions where you want "nice" errors instead of tracebacks.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            # Optional: clean exit on Ctrl+C
            logger.error("Interrupted.")
            raise SystemExit(130)
        except Exception as exc:
            # Keep message simple (good for eval output). Debug mode can enable tracebacks
            logger.error("%s", exc)
            raise SystemExit(1)

    return wrapper
6