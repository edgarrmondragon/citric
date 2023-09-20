"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

from __future__ import annotations

import typing as t
import warnings
from importlib import metadata

from citric._compat import CitricDeprecationWarning
from citric.rpc.client import RPC

if t.TYPE_CHECKING:
    from citric.rpc.client import RPC as Client  # noqa: N811, F401


__version__ = metadata.version(__package__)
"""Package version"""

del annotations, metadata

__all__ = ["RPC"]


def __getattr__(name: str) -> t.Any:  # noqa: ANN401
    if name == "Client":
        warnings.warn(
            "citric.Client is deprecated, use citric.RPC instead",
            CitricDeprecationWarning,
            stacklevel=2,
        )
        return RPC

    message = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(message)
