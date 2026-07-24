"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

from __future__ import annotations

from importlib import metadata

from citric import objects
from citric.client import Client, ServerVersion
from citric.rest import RESTClient

__version__: str = metadata.version("citric")
"""Package version"""

del annotations, metadata  # ruff: ignore[non-empty-init-module]

__all__ = ["Client", "RESTClient", "ServerVersion", "objects"]
