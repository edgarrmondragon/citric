"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

from __future__ import annotations

from importlib import metadata

from citric.client import Client
from citric.rest import RESTClient

__version__ = metadata.version("citric")
"""Package version"""

del annotations, metadata  # noqa: RUF067

__all__ = ["Client", "RESTClient"]
