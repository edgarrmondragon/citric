"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

from __future__ import annotations

from importlib import metadata

from citric.client import Client
from citric.rest import RESTClient
from citric.survey import AnswerOption, Question, QuestionL10n

__version__ = metadata.version("citric")
"""Package version"""

del annotations, metadata  # noqa: RUF067

__all__ = ["AnswerOption", "Client", "Question", "QuestionL10n", "RESTClient"]
