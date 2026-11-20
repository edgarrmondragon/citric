# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Constants shared by the clients and transports."""

from __future__ import annotations

__all__ = [
    "DEFAULT_TIMEOUT",
]

DEFAULT_TIMEOUT: float = 300.0
"""Default timeout of a request, in seconds.

Generous enough for slow operations like importing a large survey.
"""
