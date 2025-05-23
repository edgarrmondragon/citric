"""Python classes associated with LimeSurvey objects (surveys, questions, etc.)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from uuid import UUID

    from citric.types import YesNo


def to_yes_no(*, value: bool) -> YesNo:
    """Convert boolean to yes/no string."""  # noqa: DOC201
    return "Y" if value else "N"


@dataclass
class Participant:
    """Participant data."""

    firstname: str
    lastname: str
    email: str
    participant_id: UUID | None = None
    language: str | None = "en"
    blacklisted: bool = False
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of participant.
        """
        return {
            "participant_id": str(self.participant_id) if self.participant_id else None,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "language": self.language,
            "blacklisted": to_yes_no(value=self.blacklisted),
            **self.attributes,
        }
