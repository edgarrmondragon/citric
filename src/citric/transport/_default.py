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
    if transport is not None and requests_session is not None:
        err = "Both 'transport' and 'requests_session' are set; only one should be used"
        raise ValueError(err)

    if transport is None and requests_session is None:
        return requests.Session()

    if requests_session is not None:
        warnings.warn(
            "Parameter 'requests_session' is deprecated; use 'transport' instead",
            DeprecationWarning,
            stacklevel=3,
        )
        return requests_session

    return transport  # type: ignore[return-value]  # ty: ignore[invalid-return-type]
