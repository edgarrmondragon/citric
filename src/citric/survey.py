"""Question object for generating LimeSurvey LSQ import files."""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET  # noqa: S405
from dataclasses import dataclass, field


def _add_fields(parent: ET.Element, field_names: list[str]) -> None:
    fields_elem = ET.SubElement(parent, "fields")
    for name in field_names:
        ET.SubElement(fields_elem, "fieldname").text = name


def _add_val(parent: ET.Element, tag: str, value: str | None) -> ET.Element:
    elem = ET.SubElement(parent, tag)
    if value:
        elem.text = value
    return elem


DEFAULT_DB_VERSION = 641


_QUESTION_FIELDS = [
    "qid",
    "parent_qid",
    "sid",
    "gid",
    "type",
    "title",
    "preg",
    "other",
    "mandatory",
    "encrypted",
    "question_order",
    "scale_id",
    "same_default",
    "relevance",
    "modulename",
]

_L10N_FIELDS = ["id", "qid", "question", "help", "script", "language"]

_ATTR_FIELDS = ["qid", "attribute", "value", "language"]

_ANSWER_FIELDS = ["qid", "code", "sortorder", "assessment_value", "scale_id"]

_ANSWER_L10N_FIELDS = ["id", "aid", "answer", "language"]


@dataclass(slots=True)
class QuestionL10n:
    """Localization data for a question in one language."""

    question: str = ""
    help: str = ""
    script: str = ""


@dataclass(slots=True)
class AnswerOption:
    """A single answer option for a list or dropdown question."""

    code: str
    l10ns: dict[str, str]
    sort_order: int = 0
    assessment_value: int = 0
    scale_id: int = 0


@dataclass(slots=True)
class Question:
    """A LimeSurvey question that can export itself as an LSQ file.

    .. versionadded:: NEXT_VERSION
    """

    title: str
    type: str
    l10ns: dict[str, QuestionL10n]
    mandatory: bool = False
    other: bool = False
    encrypted: bool = False
    relevance: str = "1"
    scale_id: int = 0
    preg: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    subquestions: list[Question] = field(default_factory=list)
    answer_options: list[AnswerOption] = field(default_factory=list)

    def to_lsq(self, *, db_version: int = DEFAULT_DB_VERSION) -> io.BytesIO:
        """Generate an LSQ XML stream for use with client.import_question().

        Args:
            db_version: The database version to set in the generated LSQ.

        Returns:
            A BytesIO object containing the LSQ-format XML.
        """
        doc = ET.Element("document")
        ET.SubElement(doc, "LimeSurveyDocType").text = "Question"
        ET.SubElement(doc, "DBVersion").text = str(db_version)

        langs_elem = ET.SubElement(doc, "languages")
        for lang in self.l10ns:
            ET.SubElement(langs_elem, "language").text = lang

        self._build_questions(doc)
        self._build_question_l10ns(doc)

        if self.attributes:
            self._build_question_attributes(doc)

        if self.answer_options:
            self._build_answers(doc)

        ET.indent(doc)
        buffer = io.BytesIO()
        ET.ElementTree(doc).write(buffer, encoding="UTF-8", xml_declaration=True)
        buffer.seek(0)
        return buffer

    def _build_questions(self, doc: ET.Element) -> None:
        questions_elem = ET.SubElement(doc, "questions")
        _add_fields(questions_elem, _QUESTION_FIELDS)
        rows_elem = ET.SubElement(questions_elem, "rows")
        _add_question_row(rows_elem, qid=1, parent_qid=0, question=self, order=1)
        for i, sq in enumerate(self.subquestions, start=2):
            _add_question_row(rows_elem, qid=i, parent_qid=1, question=sq, order=i - 1)

    def _build_question_l10ns(self, doc: ET.Element) -> None:
        l10ns_elem = ET.SubElement(doc, "question_l10ns")
        _add_fields(l10ns_elem, _L10N_FIELDS)
        rows_elem = ET.SubElement(l10ns_elem, "rows")
        row_id = 1
        for lang, l10n in self.l10ns.items():
            _add_l10n_row(rows_elem, row_id=row_id, qid=1, lang=lang, l10n=l10n)
            row_id += 1
        for i, sq in enumerate(self.subquestions, start=2):
            for lang, l10n in sq.l10ns.items():
                _add_l10n_row(rows_elem, row_id=row_id, qid=i, lang=lang, l10n=l10n)
                row_id += 1

    def _build_question_attributes(self, doc: ET.Element) -> None:
        attrs_elem = ET.SubElement(doc, "question_attributes")
        _add_fields(attrs_elem, _ATTR_FIELDS)
        rows_elem = ET.SubElement(attrs_elem, "rows")
        for attr_name, attr_value in self.attributes.items():
            row = ET.SubElement(rows_elem, "row")
            _add_val(row, "qid", "1")
            _add_val(row, "attribute", attr_name)
            _add_val(row, "value", attr_value or None)
            _add_val(row, "language", None)

    def _build_answers(self, doc: ET.Element) -> None:
        answers_elem = ET.SubElement(doc, "answers")
        _add_fields(answers_elem, _ANSWER_FIELDS)
        answers_rows = ET.SubElement(answers_elem, "rows")

        answer_l10ns_elem = ET.SubElement(doc, "answer_l10ns")
        _add_fields(answer_l10ns_elem, _ANSWER_L10N_FIELDS)
        answer_l10ns_rows = ET.SubElement(answer_l10ns_elem, "rows")

        l10n_id = 1
        for aid, option in enumerate(self.answer_options, start=1):
            row = ET.SubElement(answers_rows, "row")
            _add_val(row, "qid", "1")
            _add_val(row, "code", option.code)
            _add_val(row, "sortorder", str(option.sort_order))
            _add_val(row, "assessment_value", str(option.assessment_value))
            _add_val(row, "scale_id", str(option.scale_id))
            for lang, answer_text in option.l10ns.items():
                l10n_row = ET.SubElement(answer_l10ns_rows, "row")
                _add_val(l10n_row, "id", str(l10n_id))
                _add_val(l10n_row, "aid", str(aid))
                _add_val(l10n_row, "answer", answer_text or None)
                _add_val(l10n_row, "language", lang)
                l10n_id += 1


def _add_question_row(
    rows_elem: ET.Element,
    qid: int,
    parent_qid: int,
    question: Question,
    order: int,
) -> None:
    row = ET.SubElement(rows_elem, "row")
    _add_val(row, "qid", str(qid))
    _add_val(row, "parent_qid", str(parent_qid))
    _add_val(row, "sid", "0")
    _add_val(row, "gid", "0")
    _add_val(row, "type", question.type)
    _add_val(row, "title", question.title)
    _add_val(row, "preg", question.preg)
    _add_val(row, "other", "Y" if question.other else "N")
    _add_val(row, "mandatory", "Y" if question.mandatory else "N")
    _add_val(row, "encrypted", "Y" if question.encrypted else "N")
    _add_val(row, "question_order", str(order))
    _add_val(row, "scale_id", str(question.scale_id))
    _add_val(row, "same_default", "0")
    _add_val(row, "relevance", question.relevance)
    _add_val(row, "modulename", None)


def _add_l10n_row(
    rows_elem: ET.Element,
    row_id: int,
    qid: int,
    lang: str,
    l10n: QuestionL10n,
) -> None:
    row = ET.SubElement(rows_elem, "row")
    _add_val(row, "id", str(row_id))
    _add_val(row, "qid", str(qid))
    _add_val(row, "question", l10n.question or None)
    _add_val(row, "help", l10n.help or None)
    _add_val(row, "script", l10n.script or None)
    _add_val(row, "language", lang)
