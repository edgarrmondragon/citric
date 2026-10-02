# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""The default HTTP transport implementation."""

from __future__ import annotations

__lazy_modules__ = {
    "requests",
    "warnings",
}

import warnings
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from citric.transport.protocol import HTTPTransport


def _transport_or_default(
    transport: HTTPTransport | None, requests_session: HTTPTransport | None
) -> HTTPTransport:
    """Resolve the transport to use, handling the deprecated ``requests_session``.

    Must be called directly from the public constructor that received the
    arguments, so that the deprecation warning is attributed to the user's call.

    Args:
        transport: The ``transport`` argument of the public constructor.
        requests_session: The deprecated ``requests_session`` argument.

    Returns:
        The given transport, or a new :py:class:`requests.Session`.

    Raises:
        TypeError: If both ``transport`` and ``requests_session`` are set.
    """
    if transport is not None and requests_session is not None:
        err = "Both 'transport' and 'requests_session' are set; only one should be used"
        raise TypeError(err)

    if requests_session is not None:
        warnings.warn(
            "Parameter 'requests_session' is deprecated; use 'transport' instead",
            DeprecationWarning,
            stacklevel=3,  # helper -> public constructor -> user code
        )
        return requests_session

    return transport if transport is not None else requests.Session()
