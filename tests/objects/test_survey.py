"""Unit tests for Survey LSS generation."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from citric.objects import (
    AnswerOption,
    Question,
    QuestionGroup,
    QuestionL10n,
    Survey,
    SurveyL10n,
)


def _parse(s: Survey) -> ET.Element:
    return ET.parse(s.to_lss()).getroot()


def test_survey_metadata():
    s = Survey(
        language="en",
        title="Test Survey",
    )
    root = _parse(s)
    assert root.tag == "document"
    assert root.findtext("LimeSurveyDocType") == "Survey"
    assert root.findtext("DBVersion") == "641"


def test_survey_metadata_custom_db_version():
    s = Survey(language="en", title="Test Survey")
    root = ET.parse(s.to_lss(db_version=700)).getroot()
    assert root.findtext("DBVersion") == "700"


def test_survey_base_language_in_languages():
    s = Survey(language="en", title="Test Survey")
    root = _parse(s)
    langs = [e.text for e in root.findall("languages/language")]
    assert langs == ["en"]


def test_survey_admin_fields():
    s = Survey(
        language="en",
        title="Test Survey",
        admin="Jane Doe",
        adminemail="jane@example.com",
        format="S",
    )
    root = _parse(s)
    survey_row = root.find("surveys/rows/row")
    assert survey_row is not None
    assert survey_row.findtext("admin") == "Jane Doe"
    assert survey_row.findtext("adminemail") == "jane@example.com"
    assert survey_row.findtext("format") == "S"


def test_survey_languagesettings_base():
    s = Survey(language="en", title="Welcome Survey")
    root = _parse(s)
    rows = root.findall("surveys_languagesettings/rows/row")
    assert len(rows) == 1
    assert rows[0].findtext("surveyls_language") == "en"
    assert rows[0].findtext("surveyls_title") == "Welcome Survey"


def test_survey_languagesettings_with_l10n():
    s = Survey(
        language="en",
        title="My Survey",
        l10ns={
            "en": SurveyL10n(
                title="My Survey",
                description="A description",
                welcometext="Welcome!",
                endtext="Thanks!",
            ),
            "fr": SurveyL10n(title="Mon Enquête", description="Une description"),
        },
    )
    root = _parse(s)

    # Both languages should appear in the <languages> block
    langs = {e.text for e in root.findall("languages/language")}
    assert langs == {"en", "fr"}

    rows = root.findall("surveys_languagesettings/rows/row")
    assert len(rows) == 2

    by_lang = {r.findtext("surveyls_language"): r for r in rows}
    assert by_lang["en"].findtext("surveyls_title") == "My Survey"
    assert by_lang["en"].findtext("surveyls_description") == "A description"
    assert by_lang["en"].findtext("surveyls_welcometext") == "Welcome!"
    assert by_lang["en"].findtext("surveyls_endtext") == "Thanks!"
    assert by_lang["fr"].findtext("surveyls_title") == "Mon Enquête"


def test_survey_l10n_falls_back_to_survey_title():
    """If base language is not in l10ns, the survey title is used."""
    s = Survey(
        language="en",
        title="Fallback Title",
        l10ns={"fr": SurveyL10n(title="Titre de secours")},
    )
    root = _parse(s)
    rows = root.findall("surveys_languagesettings/rows/row")
    by_lang = {r.findtext("surveyls_language"): r for r in rows}
    assert by_lang["en"].findtext("surveyls_title") == "Fallback Title"


def test_survey_groups_and_questions():
    q1 = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Q1?")},
    )
    group = QuestionGroup(title="Group 1", questions=[q1])
    s = Survey(language="en", title="Test Survey", groups=[group])
    root = _parse(s)

    group_rows = root.findall("groups/rows/row")
    assert len(group_rows) == 1
    assert group_rows[0].findtext("group_name") == "Group 1"

    question_rows = root.findall("questions/rows/row")
    assert len(question_rows) == 1
    assert question_rows[0].findtext("title") == "Q1"


def test_survey_multiple_groups_and_questions():
    q1 = Question(title="Q1", type="T", l10ns={"en": QuestionL10n(question="Q1?")})
    q2 = Question(title="Q2", type="T", l10ns={"en": QuestionL10n(question="Q2?")})
    q3 = Question(title="Q3", type="N", l10ns={"en": QuestionL10n(question="Q3?")})
    groups = [
        QuestionGroup(title="Group A", questions=[q1, q2]),
        QuestionGroup(title="Group B", questions=[q3]),
    ]
    s = Survey(language="en", title="Test Survey", groups=groups)
    root = _parse(s)

    group_rows = root.findall("groups/rows/row")
    assert len(group_rows) == 2
    assert group_rows[0].findtext("group_name") == "Group A"
    assert group_rows[1].findtext("group_name") == "Group B"

    question_rows = root.findall("questions/rows/row")
    assert len(question_rows) == 3
    titles = [r.findtext("title") for r in question_rows]
    assert titles == ["Q1", "Q2", "Q3"]

    # Each question row should reference sid=1
    for row in question_rows:
        assert row.findtext("sid") == "1"


def test_survey_question_l10ns():
    q = Question(
        title="Q1",
        type="T",
        l10ns={
            "en": QuestionL10n(question="What is your name?", help="Enter your name"),
            "fr": QuestionL10n(question="Quel est votre nom?"),
        },
    )
    s = Survey(
        language="en",
        title="Test Survey",
        groups=[QuestionGroup(title="G1", questions=[q])],
    )
    root = _parse(s)

    l10n_rows = root.findall("question_l10ns/rows/row")
    assert len(l10n_rows) == 2
    by_lang = {r.findtext("language"): r for r in l10n_rows}
    assert by_lang["en"].findtext("question") == "What is your name?"
    assert by_lang["en"].findtext("help") == "Enter your name"
    assert by_lang["fr"].findtext("question") == "Quel est votre nom?"


def test_survey_with_subquestions():
    sq1 = Question(
        title="SQ1",
        type="T",
        l10ns={"en": QuestionL10n(question="Row 1")},
    )
    sq2 = Question(
        title="SQ2",
        type="T",
        l10ns={"en": QuestionL10n(question="Row 2")},
    )
    q = Question(
        title="Q1",
        type="F",
        l10ns={"en": QuestionL10n(question="Matrix question")},
        subquestions=[sq1, sq2],
    )
    s = Survey(
        language="en",
        title="Test Survey",
        groups=[QuestionGroup(title="G1", questions=[q])],
    )
    root = _parse(s)

    sq_rows = root.findall("subquestions/rows/row")
    assert len(sq_rows) == 2
    titles = [r.findtext("title") for r in sq_rows]
    assert titles == ["SQ1", "SQ2"]

    # All subquestion rows should reference sid=1
    for row in sq_rows:
        assert row.findtext("sid") == "1"


def test_survey_with_answer_options():
    opt_a = AnswerOption(code="A", l10ns={"en": "Option A"}, sort_order=1)
    opt_b = AnswerOption(code="B", l10ns={"en": "Option B"}, sort_order=2)
    q = Question(
        title="Q1",
        type="L",
        l10ns={"en": QuestionL10n(question="Pick one")},
        answer_options=[opt_a, opt_b],
    )
    s = Survey(
        language="en",
        title="Test Survey",
        groups=[QuestionGroup(title="G1", questions=[q])],
    )
    root = _parse(s)

    answer_rows = root.findall("answers/rows/row")
    assert len(answer_rows) == 2
    codes = [r.findtext("code") for r in answer_rows]
    assert codes == ["A", "B"]
    assert answer_rows[0].findtext("sortorder") == "1"

    l10n_rows = root.findall("answer_l10ns/rows/row")
    assert len(l10n_rows) == 2
    assert l10n_rows[0].findtext("answer") == "Option A"
    assert l10n_rows[1].findtext("answer") == "Option B"


def test_survey_answer_options_multilingual():
    opt = AnswerOption(
        code="Y",
        l10ns={"en": "Yes", "fr": "Oui"},
    )
    q = Question(
        title="Q1",
        type="L",
        l10ns={"en": QuestionL10n(question="Yes/No?")},
        answer_options=[opt],
    )
    s = Survey(
        language="en",
        title="Test Survey",
        groups=[QuestionGroup(title="G1", questions=[q])],
    )
    root = _parse(s)

    l10n_rows = root.findall("answer_l10ns/rows/row")
    assert len(l10n_rows) == 2
    by_lang = {r.findtext("language"): r for r in l10n_rows}
    assert by_lang["en"].findtext("answer") == "Yes"
    assert by_lang["fr"].findtext("answer") == "Oui"


def test_survey_empty_groups():
    s = Survey(language="en", title="Empty Survey", groups=[])
    root = _parse(s)
    assert root.findall("groups/rows/row") == []
    assert root.findall("questions/rows/row") == []
    assert root.findall("subquestions/rows/row") == []
    assert root.findall("question_l10ns/rows/row") == []
    assert root.findall("answers/rows/row") == []
    assert root.findall("answer_l10ns/rows/row") == []


def test_survey_group_description():
    group = QuestionGroup(title="My Group", description="Group description")
    s = Survey(language="en", title="Test Survey", groups=[group])
    root = _parse(s)
    row = root.find("groups/rows/row")
    assert row is not None
    assert row.findtext("description") == "Group description"


@pytest.mark.parametrize("db_version", [500, 641, 700])
def test_survey_custom_db_version(db_version: int):
    s = Survey(language="en", title="Test")
    root = ET.parse(s.to_lss(db_version=db_version)).getroot()
    assert root.findtext("DBVersion") == str(db_version)
