"""Create and import a question using Python objects."""

from __future__ import annotations

# start example
from citric import Client
from citric.objects import AnswerOption, Question, QuestionL10n

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"

client = Client(LS_URL, "iamadmin", "secret")

survey_id = client.list_surveys()[0]["sid"]
group_id = client.list_groups(survey_id)[0]["id"]

# A simple single-choice (list) question with answer options
list_question = Question(
    title="Q01",
    type="L",
    l10ns={
        "en": QuestionL10n(question="What is your favourite colour?"),
        "es": QuestionL10n(question="Cual es tu color favorito?"),
    },
    answer_options=[
        AnswerOption(code="R", l10ns={"en": "Red", "es": "Rojo"}),
        AnswerOption(code="G", l10ns={"en": "Green", "es": "Verde"}),
        AnswerOption(code="B", l10ns={"en": "Blue", "es": "Azul"}),
    ],
)

client.import_question(list_question.to_lsq(), survey_id, group_id)

# A multiple-choice question with subquestions
mc_question = Question(
    title="Q02",
    type="M",
    l10ns={"en": QuestionL10n(question="Which of the following do you use?")},
    subquestions=[
        Question(
            title="SQ001",
            type="T",
            l10ns={"en": QuestionL10n(question="Python")},
        ),
        Question(
            title="SQ002",
            type="T",
            l10ns={"en": QuestionL10n(question="R")},
        ),
        Question(
            title="SQ003",
            type="T",
            l10ns={"en": QuestionL10n(question="Julia")},
        ),
    ],
)

client.import_question(mc_question.to_lsq(), survey_id, group_id)
# end example
