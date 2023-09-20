"""Deprecated module for the RPC session."""

from __future__ import annotations

import typing as t
import warnings

from citric._compat import CitricDeprecationWarning

if t.TYPE_CHECKING:
    from citric.rpc.method import Method  # noqa: F401


def __getattr__(name: str) -> t.Any:  # noqa: ANN401
    """Return the element from the citric.rpc.session module."""
    if not name.startswith("_"):
        warnings.warn(
            f"citric.method.{name} is deprecated, use citric.rpc.method.{name} instead",  # noqa: E501
            CitricDeprecationWarning,
            stacklevel=2,
        )
        from citric.rpc import session

        return getattr(session, name)

    message = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(message)
