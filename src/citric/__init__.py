"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

from __future__ import annotations

from importlib import metadata

from citric.client import Client

__version__ = metadata.version(__package__)
"""Package version"""

del annotations, metadata

__all__ = ["Client"]
