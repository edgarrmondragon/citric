"""Top-level package for citric."""

from __future__ import annotations

import sys

from citric.client import Client  # noqa: F401

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

__version__ = version(__name__)
"""Package version"""
