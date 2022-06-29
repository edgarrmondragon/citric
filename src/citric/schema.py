"""Schemas for LimeSurvey objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def to_yes_no(*, value: bool) -> str:
    """Convert boolean to yes/no string."""
    return "Y" if value else "N"


@dataclass
class Participant:
    """Participant data."""

    firstname: str
    lastname: str
    email: str
    participant_id: str | None = None
    language: str | None = "en"
    blacklisted: bool = False
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation of participant.
        """
        return {
            "participant_id": self.participant_id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "language": self.language,
            "blacklisted": to_yes_no(value=self.blacklisted),
            **self.attributes,
        }
