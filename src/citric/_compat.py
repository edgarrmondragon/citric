"""Compatibility functions and classes for different versions of LimeSurvey."""

from __future__ import annotations

import typing as t
import warnings
from functools import wraps

__all__ = ["FutureVersionWarning", "future", "future_parameter"]


def _warning_message(next_version: str) -> tuple[str, ...]:
    """Format a warning message.

    Args:
        next_version: The first version of LimeSurvey that this function is
            available in.

    Returns:
        The formatted warning message.
    """
    return (
        "is only supported in the current development build of ",
        f"LimeSurvey and is subject to change before version {next_version}.",
    )


class FutureVersionWarning(UserWarning):
    """Warning for features only available in an unreleased version of LimeSurvey."""


def future(version: str) -> t.Callable:
    """Mark a function as only available in the current development build of LimeSurvey.

    Args:
        version: The earliest version of LimeSurvey that this function is
            available in.

    Returns:
        The wrapped function.
    """
    message = _warning_message(version)

    def decorate(fn: t.Callable) -> t.Callable:
        @wraps(fn)
        def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Callable:
            warnings.warn(
                f"Method {fn.__name__} {''.join(message)}",
                FutureVersionWarning,
                stacklevel=2,
            )
            return fn(*args, **kwargs)

        return wrapper

    return decorate


def future_parameter(version: str, parameter: str) -> t.Callable:
    """Mark a function as only available in the current development build of LimeSurvey.

    Args:
        version: The earliest version of LimeSurvey that this parameter is
            available in.
        parameter: The parameter that is only available in the current development
            build of LimeSurvey.

    Returns:
        The wrapped function.
    """
    message = _warning_message(version)

    def decorate(fn: t.Callable) -> t.Callable:
        @wraps(fn)
        def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Callable:
            if parameter in kwargs:
                warnings.warn(
                    f"Parameter {parameter} {''.join(message)}",
                    FutureVersionWarning,
                    stacklevel=2,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorate
