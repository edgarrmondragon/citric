"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

from __future__ import annotations

import sys

from citric.client import Client

if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__version__ = metadata.version(__package__)
"""Package version"""

del annotations, metadata, sys

__all__ = ["Client"]
