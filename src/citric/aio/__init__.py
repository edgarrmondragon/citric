# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Asynchronous API for LimeSurvey RemoteControl 2.

.. versionadded:: NEXT_VERSION
"""

from __future__ import annotations

__lazy_modules__ = {
    "citric.aio.client",
    "citric.aio.session",
}

from citric.aio.client import AsyncClient
from citric.aio.session import AsyncSession

__all__ = [
    "AsyncClient",
    "AsyncSession",
]
