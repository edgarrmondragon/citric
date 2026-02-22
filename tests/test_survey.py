"""Unit tests for Question LSQ generation."""

from __future__ import annotations

import xml.etree.ElementTree as ET  # noqa: S405

from citric.survey import AnswerOption, Question, QuestionL10n


def _parse(q: Question) -> ET.Element:
    return ET.parse(q.to_lsq()).getroot()  # noqa: S314


def test_document_metadata():
    """Test that the document root has the correct metadata."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Hello")},
    )
    root = _parse(q)
    assert root.tag == "document"
    assert root.findtext("LimeSurveyDocType") == "Question"
    assert root.findtext("DBVersion") == "641"
    langs = [e.text for e in root.findall("languages/language")]
    assert langs == ["en"]


def test_simple_text_question():
    """Test a simple text question with no subquestions or answer options."""
    q = Question(
        title="G01Q01",
        type="T",
        l10ns={"en": QuestionL10n(question="What is your name?")},
    )
    root = _parse(q)

    rows = root.findall("questions/rows/row")
    assert len(rows) == 1
    row = rows[0]
    assert row.findtext("qid") == "1"
    assert row.findtext("parent_qid") == "0"
    assert row.findtext("type") == "T"
    assert row.findtext("title") == "G01Q01"
    assert row.findtext("mandatory") == "N"
    assert row.findtext("other") == "N"
    assert row.findtext("encrypted") == "N"
    assert row.findtext("relevance") == "1"

    l10n_rows = root.findall("question_l10ns/rows/row")
    assert len(l10n_rows) == 1
    assert l10n_rows[0].findtext("qid") == "1"
    assert l10n_rows[0].findtext("question") == "What is your name?"
    assert l10n_rows[0].findtext("language") == "en"

    assert root.find("question_attributes") is None
    assert root.find("answers") is None


def test_empty_attributes_omits_section():
    """Test that an empty attributes dict omits the question_attributes section."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Hello")},
        attributes={},
    )
    assert _parse(q).find("question_attributes") is None


def test_list_question_with_answer_options():
    """Test a list question with answer options and a question attribute."""
    q = Question(
        title="Q1",
        type="L",
        l10ns={"en": QuestionL10n(question="Pick one")},
        attributes={"answer_order": "random"},
        answer_options=[
            AnswerOption(code="A1", l10ns={"en": "Yes"}, sort_order=1),
            AnswerOption(code="A2", l10ns={"en": "No"}, sort_order=2),
        ],
    )
    root = _parse(q)

    attr_rows = root.findall("question_attributes/rows/row")
    assert len(attr_rows) == 1
    assert attr_rows[0].findtext("attribute") == "answer_order"
    assert attr_rows[0].findtext("value") == "random"

    answer_rows = root.findall("answers/rows/row")
    assert len(answer_rows) == 2
    assert answer_rows[0].findtext("code") == "A1"
    assert answer_rows[0].findtext("sortorder") == "1"
    assert answer_rows[1].findtext("code") == "A2"
    assert answer_rows[1].findtext("sortorder") == "2"

    l10n_rows = root.findall("answer_l10ns/rows/row")
    assert len(l10n_rows) == 2
    assert l10n_rows[0].findtext("answer") == "Yes"
    assert l10n_rows[0].findtext("language") == "en"
    assert l10n_rows[1].findtext("answer") == "No"


def test_multiple_choice_with_subquestions():
    """Test a multiple-choice question with two subquestions."""
    q = Question(
        title="Q1",
        type="M",
        l10ns={"en": QuestionL10n(question="Which apply?")},
        subquestions=[
            Question(
                title="SQ001",
                type="T",
                l10ns={"en": QuestionL10n(question="Option A")},
            ),
            Question(
                title="SQ002",
                type="T",
                l10ns={"en": QuestionL10n(question="Option B")},
            ),
        ],
    )
    root = _parse(q)

    question_rows = root.findall("questions/rows/row")
    assert len(question_rows) == 3

    assert question_rows[0].findtext("qid") == "1"
    assert question_rows[0].findtext("parent_qid") == "0"
    assert question_rows[0].findtext("title") == "Q1"

    assert question_rows[1].findtext("parent_qid") == "1"
    assert question_rows[1].findtext("title") == "SQ001"

    assert question_rows[2].findtext("parent_qid") == "1"
    assert question_rows[2].findtext("title") == "SQ002"

    l10n_rows = root.findall("question_l10ns/rows/row")
    assert len(l10n_rows) == 3
    assert l10n_rows[0].findtext("question") == "Which apply?"
    assert l10n_rows[1].findtext("question") == "Option A"
    assert l10n_rows[2].findtext("question") == "Option B"

    assert root.find("answers") is None


def test_html_content_entities():
    """Test that HTML content in question text round-trips correctly through XML."""
    html = "Text with <strong>bold</strong> & 'quotes'"
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question=html)},
    )
    root = _parse(q)
    l10n_row = root.find("question_l10ns/rows/row")
    assert l10n_row is not None
    assert l10n_row.findtext("question") == html


def test_mandatory_question():
    """Test that mandatory=True produces 'Y' in the XML output."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Required")},
        mandatory=True,
    )
    root = _parse(q)
    row = root.find("questions/rows/row")
    assert row is not None
    assert row.findtext("mandatory") == "Y"


def test_xml_declaration():
    """Test that the output contains an XML declaration with UTF-8 encoding."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Hello")},
    )
    content = q.to_lsq().read()
    assert content.startswith(b"<?xml")
    assert b"UTF-8" in content


def test_fields_element_present():
    """Test that the questions section contains a fields element with expected names."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Hello")},
    )
    root = _parse(q)
    fieldnames = [e.text for e in root.findall("questions/fields/fieldname")]
    assert "qid" in fieldnames
    assert "parent_qid" in fieldnames
    assert "type" in fieldnames
    assert "title" in fieldnames


def test_multilanguage():
    """Test that multiple languages produce correct rows in questions and l10ns."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={
            "en": QuestionL10n(question="Hello"),
            "de": QuestionL10n(question="Hallo"),
        },
    )
    root = _parse(q)
    langs = [e.text for e in root.findall("languages/language")]
    assert langs == ["en", "de"]

    l10n_rows = root.findall("question_l10ns/rows/row")
    assert len(l10n_rows) == 2
    assert l10n_rows[0].findtext("language") == "en"
    assert l10n_rows[1].findtext("language") == "de"


def test_preg_empty_is_self_closing():
    """Test that a None preg field produces a self-closing element."""
    q = Question(
        title="Q1",
        type="T",
        l10ns={"en": QuestionL10n(question="Hello")},
        preg=None,
    )
    root = _parse(q)
    row = root.find("questions/rows/row")
    assert row is not None
    preg_elem = row.find("preg")
    assert preg_elem is not None
    assert preg_elem.text is None


def test_answer_aid_sequential():
    """Test that answer_l10ns rows reference sequential aid values."""
    q = Question(
        title="Q1",
        type="L",
        l10ns={"en": QuestionL10n(question="Pick one")},
        answer_options=[
            AnswerOption(code="A1", l10ns={"en": "Yes"}),
            AnswerOption(code="A2", l10ns={"en": "No"}),
            AnswerOption(code="A3", l10ns={"en": "Maybe"}),
        ],
    )
    root = _parse(q)
    l10n_rows = root.findall("answer_l10ns/rows/row")
    aids = [r.findtext("aid") for r in l10n_rows]
    assert aids == ["1", "2", "3"]
