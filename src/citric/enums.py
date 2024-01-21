"""Useful enums."""

from __future__ import annotations

import enum

__all__ = [
    "EmailSendStrategy",
    "HeadingType",
    "ImportGroupType",
    "ImportSurveyType",
    "NewSurveyType",
    "QuotaAction",
    "ResponseType",
    "ResponsesExportFormat",
    "StatisticsExportFormat",
    "StringEnum",
    "SurveyCompletionStatus",
    "TimelineAggregationPeriod",
]


class StringEnum(str, enum.Enum):
    """Enum with string values."""

    __slots__ = ()


class ImportGroupType(StringEnum):
    """Group file type."""

    LSG = "lsg"
    CSV = "csv"


class ImportSurveyType(StringEnum):
    """Survey file type."""

    LSS = "lss"
    CSV = "csv"
    TXT = "txt"
    LSA = "lsa"


class NewSurveyType(StringEnum):
    """New survey type."""

    ALL_ON_ONE_PAGE = "A"
    GROUP_BY_GROUP = "G"
    SINGLE_QUESTIONS = "S"


class StatisticsExportFormat(StringEnum):
    """Statistics export type."""

    PDF = "pdf"
    XLS = "xls"
    HTML = "html"


class ResponsesExportFormat(StringEnum):
    """Responses export type."""

    PDF = "pdf"
    CSV = "csv"
    XLS = "xls"
    DOC = "doc"
    JSON = "json"


class SurveyCompletionStatus(StringEnum):
    """Survey completion status values."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    ALL = "all"


class HeadingType(StringEnum):
    """Types of heading in responses export."""

    CODE = "code"
    FULL = "full"
    ABBREVIATED = "abbreviated"


class ResponseType(StringEnum):
    """Types of responses in export."""

    LONG = "long"
    SHORT = "short"


class TimelineAggregationPeriod(StringEnum):
    """Timeline aggregation level."""

    HOUR = "hour"
    DAY = "day"


class QuotaAction(StringEnum):
    """Quota action."""

    TERMINATE = "terminate"
    CONFIRM_TERMINATE = "confirm_terminate"

    @property
    def integer_value(self) -> int:
        """Return database value of the action.

        Returns:
            Database value of the action.
        """
        mapping = {
            self.TERMINATE: 1,
            self.CONFIRM_TERMINATE: 2,
        }
        return mapping[self]


class EmailSendStrategy(enum.IntEnum):
    """Email send flag."""

    PENDING = 1
    RESEND = 2

    @classmethod
    def to_flag(cls: type[EmailSendStrategy], value: int) -> bool:
        """Return the flag for this email send enum."""
        return value == cls.PENDING
