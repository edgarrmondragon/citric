"""Mailpit API client."""

from __future__ import annotations

import requests


class MailpitClient:
    """Mailpit API client."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_all(self) -> dict:
        """Get all messages."""
        return requests.get(f"{self.base_url}/api/v1/messages", timeout=10).json()

    def delete(self) -> None:
        """Delete all messages."""
        requests.delete(
            f"{self.base_url}/api/v1/messages",
            timeout=10,
            params={"query": "after:2024/04/01"},
        )
