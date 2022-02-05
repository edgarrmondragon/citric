"""Top-level package for citric."""
from citric.client import Client  # noqa: F401

try:
    from importlib.metadata import version  # type: ignore
except ImportError:
    from importlib_metadata import version  # type: ignore

__version__ = version(__name__)
"""Package version"""
