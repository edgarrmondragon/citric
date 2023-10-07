from __future__ import annotations

from importlib import metadata


def get_citric_user_agent() -> str:
    """Get the citric user agent."""
    return f"citric/{metadata.version('citric')}"
