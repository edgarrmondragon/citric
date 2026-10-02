# Copyright (c) 2026 Edgar Ramírez-Mondragón

__lazy_modules__ = {
    "collections",
    "collections.abc",
    "functools",
    "typing",
    "warnings",
}

import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


def deprecate_requests_session(fn: Callable[P, T]) -> Callable[P, T]:
    old = "requests_session"
    new = "transport"

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # ruff: ignore[any-type]
        if new not in kwargs and (depr := kwargs.pop(old, None)) is not None:
            warnings.warn(
                f"Parameter '{old}' is deprecated; use '{new}' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            kwargs[new] = depr

        return fn(*args, **kwargs)

    return wrapper
