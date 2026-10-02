# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""The default HTTP transport implementation."""

from __future__ import annotations

__lazy_modules__ = {
    "requests",
}

from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from citric.transport.protocol import HTTPTransport


def _transport_or_default(transport: HTTPTransport | None) -> HTTPTransport:
    return transport if transport is not None else requests.session()
