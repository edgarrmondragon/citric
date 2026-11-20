# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Create and import a survey using Python objects."""

from __future__ import annotations

# start example
from citric import Client
from citric.enums import QuestionType
from citric.objects import (
    AnswerOption,
    Question,
    QuestionGroup,
    QuestionL10n,
    Survey,
    SurveyL10n,
)

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

client = Client(LS_URL, "iamadmin", "secret")

survey = Survey(
    language="en",
    title="Customer feedback",
    l10ns={"es": SurveyL10n(title="Tu opinión")},
    groups=[
        QuestionGroup(
            title="About you",
            questions=[
                Question(
                    title="Q01",
                    type=QuestionType.RADIO_BUTTONS_LIST,
                    l10ns={
                        "en": QuestionL10n(question="How did you find us?"),
                        "es": QuestionL10n(question="¿Cómo nos encontraste?"),
                    },
                    answer_options=[
                        AnswerOption(code="WEB", l10ns={"en": "Web", "es": "Web"}),
                        AnswerOption(
                            code="FRD",
                            l10ns={"en": "A friend", "es": "Un amigo"},
                        ),
                    ],
                ),
            ],
        ),
        QuestionGroup(
            title="Your feedback",
            questions=[
                Question(
                    title="Q02",
                    type=QuestionType.LONG_FREE_TEXT,
                    l10ns={
                        "en": QuestionL10n(question="Anything else to tell us?"),
                        "es": QuestionL10n(question="¿Algo más que contarnos?"),
                    },
                ),
            ],
        ),
    ],
)

survey_id = client.import_survey(survey.to_lss())
# end example
