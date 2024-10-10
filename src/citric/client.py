"""Deprecated module for the RPC client."""

from __future__ import annotations

import typing as t
import warnings

from citric._compat import CitricDeprecationWarning

if t.TYPE_CHECKING:
    from citric.rpc.client import (  # noqa: F401
        RPC,
        FileMetadata,
        QuestionReference,
        UploadedFile,
    )

    Client = RPC


def __getattr__(name: str) -> t.Any:  # noqa: ANN401
    """Return the element from the citric.rpc.client module."""
    if not name.startswith("_"):
        warnings.warn(
            f"citric.client.{name} is deprecated, use citric.rpc.client.{name} instead",
            CitricDeprecationWarning,
            stacklevel=2,
        )
        from citric.rpc import client  # noqa: PLC0415

        return getattr(client, name)

    message = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(message)
