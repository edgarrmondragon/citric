# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Common reusable functions."""

from __future__ import annotations

__lazy_modules__ = {"importlib"}

from functools import cache
from importlib import metadata


@cache
def _get_user_agent(val: str | None) -> str:
    return val or f"citric/{metadata.version('citric')}"
