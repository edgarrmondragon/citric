# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Python classes associated with LimeSurvey objects (surveys, questions, etc.)."""

__lazy_modules__ = {
    "citric.objects._participant",
    "citric.objects._question",
}

from ._participant import MailOutcome, MailParticipantOutcome, Participant, to_yes_no
from ._question import AnswerOption, Question, QuestionL10n

__all__ = [
    "AnswerOption",
    "MailOutcome",
    "MailParticipantOutcome",
    "Participant",
    "Question",
    "QuestionL10n",
    "to_yes_no",
]
