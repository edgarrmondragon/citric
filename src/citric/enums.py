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

    #: Include only incomplete answers
    COMPLETE = "complete"

    #: Only include incomplete answers
    INCOMPLETE = "incomplete"

    #: Include ALL answers
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
    """Terminate after related visible question was submitted."""

    CONFIRM_TERMINATE = "confirm_terminate"
    """Soft terminate after related visible question was submitted, answer will be
    editable."""

    TERMINATE_VISIBLE_HIDDEN = "terminate_visible_hidden"
    """Terminate after related visible and hidden questions were submitted.

    .. versionadded:: NEXT_VERSION
    .. minlimesurveyattribute:: 6.6.7
    """

    TERMINATE_PAGES = "terminate_pages"
    """Terminate after all page submissions.

    .. versionadded:: NEXT_VERSION
    .. minlimesurveyattribute:: 6.6.7
    """

    @property
    def integer_value(self) -> int:
        """Return database value of the action.

        Returns:
            Database value of the action.
        """
        mapping = {
            self.TERMINATE: 1,
            self.CONFIRM_TERMINATE: 2,
            self.TERMINATE_VISIBLE_HIDDEN: 3,
            self.TERMINATE_PAGES: 4,
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
