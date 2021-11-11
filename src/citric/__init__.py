"""Top-level package for citric."""
from citric.client import Client  # noqa: F401

try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore


try:
    __version__ = version(__name__)
    """Package version"""
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
    """Package version"""
