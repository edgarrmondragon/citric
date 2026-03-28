"""Survey object for generating LimeSurvey LSS import files."""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from citric.objects._question import (
    Question, 
    _add_fields, 
    _add_val, 
    DEFAULT_DB_VERSION, 
    _QUESTION_FIELDS, 
    _L10N_FIELDS, 
    _SUBQUESTION_FIELDS, 
    _ATTR_FIELDS, 
    _ANSWER_FIELDS, 
    _ANSWER_L10N_FIELDS,
    _add_question_row,
    _add_subquestion_row,
    _add_l10n_row
)

_SURVEY_FIELDS = [
    "sid",
    "gsid",
    "admin",
    "expires",
    "startdate",
    "adminemail",
    "anonymized",
    "faxto",
    "format",
    "savetimings",
    "template",
    "language",
    "additional_languages",
    "datestamp",
    "usecookie",
    "allowregister",
    "allowsave",
    "autonumber_start",
    "autoredirect",
    "allowprev",
    "printanswers",
    "ipaddr",
    "ipanonymize",
    "refurl",
    "showsurveypolicynotice",
    "publicstatistics",
    "publicgraphs",
    "listpublic",
    "htmlemail",
    "sendconfirmation",
    "tokenanswerspersistence",
    "assessments",
    "usecaptcha",
    "usetokens",
    "bounce_email",
    "attributedescriptions",
    "emailresponseto",
    "emailnotificationto",
    "tokenlength",
    "showxquestions",
    "showgroupinfo",
    "shownoanswer",
    "showqnumcode",
    "bouncetime",
    "bounceprocessing",
    "bounceaccounttype",
    "bounceaccounthost",
    "bounceaccountpass",
    "bounceaccountencryption",
    "bounceaccountuser",
    "showwelcomeinfo",
    "showprogress",
    "questionindex",
    "navigationdelay",
    "nokeyboard",
    "alloweditaftercompletion",
    "googleanalyticsstyle",
    "googleanalyticsapikey",
    "tokenencryptionoptions",
]

_SURVEY_L10N_FIELDS = [
    "surveyls_survey_id",
    "surveyls_language",
    "surveyls_title",
    "surveyls_description",
    "surveyls_welcometext",
    "surveyls_endtext",
    "surveyls_policy_notice",
    "surveyls_policy_error",
    "surveyls_policy_notice_label",
    "surveyls_url",
    "surveyls_urldescription",
    "surveyls_email_invite_subj",
    "surveyls_email_invite",
    "surveyls_email_remind_subj",
    "surveyls_email_remind",
    "surveyls_email_register_subj",
    "surveyls_email_register",
    "surveyls_email_confirm_subj",
    "surveyls_email_confirm",
    "surveyls_dateformat",
    "surveyls_attributecaptions",
    "email_admin_notification_subj",
    "email_admin_notification",
    "email_admin_responses_subj",
    "email_admin_responses",
    "surveyls_numberformat",
    "attachments",
]

_GROUP_FIELDS = ["gid", "sid", "group_name", "group_order", "description", "language", "randomization_group", "grelevance"]

@dataclass(slots=True)
class SurveyL10n:
    """Localization data for a survey in one language."""

    title: str = ""
    description: str = ""
    welcometext: str = ""
    endtext: str = ""

@dataclass(slots=True)
class QuestionGroup:
    """A LimeSurvey question group."""
    title: str
    description: str = ""
    questions: list[Question] = field(default_factory=list)

@dataclass(slots=True)
class Survey:
    """A LimeSurvey survey that can export itself as an LSS file."""

    language: str
    title: str
    l10ns: dict[str, SurveyL10n] = field(default_factory=dict)
    admin: str = "Administrator"
    adminemail: str = "admin@example.com"
    format: str = "G"
    groups: list[QuestionGroup] = field(default_factory=list)

    def to_lss(self, *, db_version: int = DEFAULT_DB_VERSION) -> io.BytesIO:
        """Generate an LSS XML stream for use with client.import_survey()."""
        doc = ET.Element("document")
        ET.SubElement(doc, "LimeSurveyDocType").text = "Survey"
        ET.SubElement(doc, "DBVersion").text = str(db_version)

        langs_elem = ET.SubElement(doc, "languages")
        ET.SubElement(langs_elem, "language").text = self.language
        for lang in self.l10ns:
            if lang != self.language:
                ET.SubElement(langs_elem, "language").text = lang

        self._build_surveys(doc)
        self._build_surveys_languagesettings(doc)
        self._build_groups(doc)
        self._build_questions(doc)
        self._build_subquestions(doc)
        self._build_question_l10ns(doc)
        self._build_answers(doc)
        
        ET.indent(doc)
        buffer = io.BytesIO()
        ET.ElementTree(doc).write(buffer, encoding="UTF-8", xml_declaration=True)
        buffer.seek(0)
        return buffer

    def _build_surveys(self, doc: ET.Element) -> None:
        elem = ET.SubElement(doc, "surveys")
        _add_fields(elem, _SURVEY_FIELDS)
        rows_elem = ET.SubElement(elem, "rows")
        row = ET.SubElement(rows_elem, "row")
        _add_val(row, "sid", "1")
        _add_val(row, "gsid", "1")
        _add_val(row, "admin", self.admin)
        _add_val(row, "adminemail", self.adminemail)
        _add_val(row, "language", self.language)
        _add_val(row, "format", self.format)

    def _build_surveys_languagesettings(self, doc: ET.Element) -> None:
        elem = ET.SubElement(doc, "surveys_languagesettings")
        _add_fields(elem, _SURVEY_L10N_FIELDS)
        rows_elem = ET.SubElement(elem, "rows")
        
        base_l10n = self.l10ns.get(self.language, SurveyL10n(title=self.title))
        self._add_l10n_row(rows_elem, self.language, base_l10n)
        
        for lang, l10n in self.l10ns.items():
            if lang != self.language:
                self._add_l10n_row(rows_elem, lang, l10n)

    def _add_l10n_row(self, rows_elem: ET.Element, lang: str, l10n: SurveyL10n) -> None:
        row = ET.SubElement(rows_elem, "row")
        _add_val(row, "surveyls_survey_id", "1")
        _add_val(row, "surveyls_language", lang)
        _add_val(row, "surveyls_title", l10n.title or self.title)
        _add_val(row, "surveyls_description", l10n.description)
        _add_val(row, "surveyls_welcometext", l10n.welcometext)
        _add_val(row, "surveyls_endtext", l10n.endtext)

    def _build_groups(self, doc: ET.Element) -> None:
        elem = ET.SubElement(doc, "groups")
        _add_fields(elem, _GROUP_FIELDS)
        rows_elem = ET.SubElement(elem, "rows")
        for i, group in enumerate(self.groups, start=1):
            row = ET.SubElement(rows_elem, "row")
            _add_val(row, "gid", str(i))
            _add_val(row, "sid", "1")
            _add_val(row, "group_name", group.title)
            _add_val(row, "group_order", str(i))
            _add_val(row, "description", group.description)
            _add_val(row, "language", self.language)
            _add_val(row, "randomization_group", "")
            _add_val(row, "grelevance", "1")

    def _build_questions(self, doc: ET.Element) -> None:
        questions_elem = ET.SubElement(doc, "questions")
        _add_fields(questions_elem, _QUESTION_FIELDS)
        rows_elem = ET.SubElement(questions_elem, "rows")
        
        qid = 1
        for gid, group in enumerate(self.groups, start=1):
            for order, question in enumerate(group.questions, start=1):
                row = ET.SubElement(rows_elem, "row")
                from citric.objects._question import _add_base_question_fields
                _add_base_question_fields(row, qid, 0, str(gid), question, order)
                # Ensure we set sid in the LSS export
                row.find("sid").text = "1"
                qid += 1

    def _build_subquestions(self, doc: ET.Element) -> None:
        subquestions_elem = ET.SubElement(doc, "subquestions")
        _add_fields(subquestions_elem, _SUBQUESTION_FIELDS)
        rows_elem = ET.SubElement(subquestions_elem, "rows")
        
        qid = 1
        sqid = 1000  # Offset to avoid conflict
        l10n_id = 1
        for gid, group in enumerate(self.groups, start=1):
            for question in group.questions:
                for i, sq in enumerate(question.subquestions, start=1):
                    for lang, l10n in sq.l10ns.items():
                        row = ET.SubElement(rows_elem, "row")
                        from citric.objects._question import _add_base_question_fields
                        _add_base_question_fields(
                            row,
                            sqid,
                            qid,
                            str(gid),
                            sq,
                            i,
                        )
                        row.find("sid").text = "1"
                        _add_val(row, "id", str(l10n_id))
                        _add_val(row, "question", l10n.question or None)
                        _add_val(row, "help", l10n.help or None)
                        _add_val(row, "script", l10n.script or None)
                        _add_val(row, "language", lang)
                        l10n_id += 1
                        sqid += 1
                qid += 1

    def _build_question_l10ns(self, doc: ET.Element) -> None:
        l10ns_elem = ET.SubElement(doc, "question_l10ns")
        _add_fields(l10ns_elem, _L10N_FIELDS)
        rows_elem = ET.SubElement(l10ns_elem, "rows")
        
        qid = 1
        row_id = 1
        for group in self.groups:
            for question in group.questions:
                for lang, l10n in question.l10ns.items():
                    _add_l10n_row(rows_elem, row_id=row_id, qid=qid, lang=lang, l10n=l10n)
                    row_id += 1
                qid += 1

    def _build_answers(self, doc: ET.Element) -> None:
        answers_elem = ET.SubElement(doc, "answers")
        _add_fields(answers_elem, _ANSWER_FIELDS)
        answers_rows = ET.SubElement(answers_elem, "rows")

        answer_l10ns_elem = ET.SubElement(doc, "answer_l10ns")
        _add_fields(answer_l10ns_elem, _ANSWER_L10N_FIELDS)
        answer_l10ns_rows = ET.SubElement(answer_l10ns_elem, "rows")

        qid = 1
        aid = 1
        l10n_id = 1
        for group in self.groups:
            for question in group.questions:
                for option in question.answer_options:
                    row = ET.SubElement(answers_rows, "row")
                    _add_val(row, "aid", str(aid))
                    _add_val(row, "qid", str(qid))
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
                    aid += 1
                qid += 1

