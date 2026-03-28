"""Unit tests for Survey LSS generation."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from citric.objects import Survey, SurveyL10n, QuestionGroup, Question, QuestionL10n, AnswerOption

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
    
def test_survey_groups_and_questions():
    q1 = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Q1?")},
    )
    group = QuestionGroup(title="Group 1", questions=[q1])
    s = Survey(
        language="en",
        title="Test Survey",
        groups=[group]
    )
    root = _parse(s)
    
    group_rows = root.findall("groups/rows/row")
    assert len(group_rows) == 1
    assert group_rows[0].findtext("group_name") == "Group 1"
    
    question_rows = root.findall("questions/rows/row")
    assert len(question_rows) == 1
    assert question_rows[0].findtext("title") == "Q1"
