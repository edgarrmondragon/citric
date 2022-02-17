"""Useful enums."""

from __future__ import annotations

import enum


class ImportGroupType(str, enum.Enum):
    """Group file type."""

    LSG = "lsg"
    CSV = "csv"


class ImportSurveyType(str, enum.Enum):
    """Survey file type."""

    LSS = "lss"
    CSV = "csv"
    TXT = "txt"
    LSA = "lsa"


class NewSurveyType(str, enum.Enum):
    """New survey type."""

    ALL_ON_ONE_PAGE = "A"
    GROUP_BY_GROUP = "G"
    SINGLE_QUESTIONS = "S"


class StatisticsExportFormat(str, enum.Enum):
    """Statistics export type."""

    PDF = "pdf"
    XLS = "xls"
    HTML = "html"


class ResponsesExportFormat(str, enum.Enum):
    """Responses export type."""

    PDF = "pdf"
    CSV = "csv"
    XLS = "xls"
    DOC = "doc"
    JSON = "json"


class SurveyCompletionStatus(str, enum.Enum):
    """Survey completion status values."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    ALL = "all"


class HeadingType(str, enum.Enum):
    """Types of heading in responses export."""

    CODE = "code"
    FULL = "full"
    ABBREVIATED = "abbreviated"


class ResponseType(str, enum.Enum):
    """Types of responses in export."""

    LONG = "long"
    SHORT = "short"


class TimelineAggregationPeriod(str, enum.Enum):
    """Timeline aggregation level."""

    HOUR = "hour"
    DAY = "day"
