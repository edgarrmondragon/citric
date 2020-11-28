"""Useful enums."""

import enum


class ImportSurveyType(str, enum.Enum):
    """Survey file type."""

    LSS = "lss"
    CSV = "csv"
    TXT = "txt"
    LSA = "lsa"


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
