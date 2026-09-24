# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Python classes associated with LimeSurvey objects (surveys, questions, etc.)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from uuid import UUID

    from citric.types import YesNo


def to_yes_no(*, value: bool) -> YesNo:
    """Convert boolean to yes/no string."""  # ruff: ignore[docstring-missing-returns]
    return "Y" if value else "N"


@dataclass
class Participant:
    """Participant data.

    .. versionadded:: 0.7.0
    """

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


@dataclass
class MailParticipantOutcome:
    """Individual outcome of sending an email to a participant.

    .. versionadded:: NEXT_VERSION
    """

    name: str
    email: str
    status: Literal["OK", "fail"]
    warning: Any | None
    error: str | None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MailParticipantOutcome:
        return cls(
            name=d["name"],
            email=d["email"],
            status=d["status"],
            warning=d["warning"],
            error=d["error"],
        )


@dataclass
class MailOutcome:
    """Overall outcome of sending an email to a list of participants.

    .. versionadded:: NEXT_VERSION
    """

    status: str
    participants: dict[str, MailParticipantOutcome]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MailOutcome:
        status = d.pop("status")
        return cls(
            status=status,
            participants={
                token: MailParticipantOutcome.from_dict(data)
                for token, data in d.items()
            },
        )
