"""Citric Python types."""

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 10):
        from typing import TypeAlias  # noqa: ICN003
    else:
        from typing_extensions import TypeAlias

    from citric import enums

__all__ = [
    "Result",
    "FileUploadResult",
    "GroupProperties",
    "LanguageProperties",
    "OperationStatus",
    "QuestionsListElement",
    "QuestionProperties",
    "QuotaListElement",
    "QuotaProperties",
    "RPCResponse",
    "SetQuotaPropertiesResult",
    "SurveyProperties",
    "SurveyUserActivationSettings",
    "CPDBParticipantImportResult",
]

Result: TypeAlias = t.Any
YesNo: TypeAlias = t.Literal["Y", "N", "I"]


class FileUploadResult(t.TypedDict):
    """File upload result."""

    success: bool
    size: int
    name: str
    ext: str
    filename: str
    msg: str


class GroupProperties(t.TypedDict, total=False):
    """Group properties."""

    gid: int
    sid: int
    group_order: int
    randomization_group: str
    grelevance: str
    group_name: str
    description: str


class LanguageProperties(t.TypedDict, total=False):
    """Language properties."""

    surveyls_survey_id: int
    surveyls_language: str
    surveyls_title: str
    surveyls_description: str | None
    surveyls_welcometext: str | None
    surveyls_endtext: str | None

    surveyls_policy_notice: str | None
    surveyls_policy_error: str | None
    surveyls_policy_notice_label: str | None

    surveyls_url: str
    surveyls_urldescription: str | None

    surveyls_email_invite_subj: str
    surveyls_email_invite: str
    surveyls_email_remind_subj: str
    surveyls_email_remind: str
    surveyls_email_register_subj: str
    surveyls_email_register: str
    surveyls_email_confirm_subj: str
    surveyls_email_confirm: str

    surveyls_dateformat: int
    surveyls_numberformat: int
    surveyls_attributecaptions: str | None

    email_admin_notification_subj: str
    email_admin_notification: str
    email_admin_responses_subj: str
    email_admin_responses: str

    attachments: str | None


class OperationStatus(t.TypedDict):
    """Delete language result."""

    status: str


class QuestionsListElement(t.TypedDict):
    """List questions result."""

    id: int
    qid: int
    parent_qid: int
    gid: int
    sid: int

    question: str
    help: str
    language: str

    type: str
    title: str
    preg: str
    other: YesNo
    mandatory: YesNo
    encrypted: YesNo
    question_order: int
    scale_id: int
    same_default: int
    relevance: str
    question_theme_name: str
    modulename: str
    same_script: int


class QuestionProperties(t.TypedDict, total=False):
    """Question properties result."""

    qid: int
    parent_qid: int
    gid: int
    sid: int

    type: str
    title: str
    preg: str
    other: YesNo
    mandatory: YesNo
    encrypted: YesNo
    question_order: int
    scale_id: int
    same_default: int
    relevance: str
    question_theme_name: str
    modulename: str
    same_script: int

    available_answers: t.Any
    answer_options: t.Any
    subquestions: t.Any
    default_values: t.Any

    attributes: dict[str, t.Any]
    attributes_lang: dict[str, t.Any]


class QuotaListElement(t.TypedDict):
    """List quotas result."""

    id: int
    name: str
    action: int
    limit: int
    active: int
    autoload_url: int


class QuotaProperties(t.TypedDict, total=False):
    """Quota properties result."""

    id: int
    sid: int
    name: str
    qlimit: int
    action: int
    active: int
    autoload_url: int


class RPCResponse(t.TypedDict):
    """RPC response payload."""

    id: int
    result: Result
    error: str | None


class SetQuotaPropertiesResult(t.TypedDict):
    """Set quota properties result."""

    success: bool
    message: QuotaProperties


class SurveyProperties(t.TypedDict, total=False):
    """Survey properties result."""

    sid: int
    owner_id: int
    gsid: int
    active: YesNo
    expires: str | None
    startdate: str | None
    anonymized: YesNo
    faxto: str
    format: enums.NewSurveyType
    savetiming: YesNo
    template: str
    datesstamp: YesNo
    usecookie: YesNo
    allowregister: YesNo
    allowsave: YesNo
    autonumber_start: int
    autoredirect: YesNo
    allowprev: YesNo
    printanswers: YesNo
    ipaddr: YesNo
    ipanonymize: YesNo
    refurl: YesNo
    datecreated: str
    showsurveypolicynotice: YesNo
    publicstatistics: YesNo
    publicgraphs: YesNo
    listpublic: YesNo
    tokenanswerspersistence: YesNo
    assessments: YesNo
    usecaptcha: YesNo
    usetokens: YesNo
    attributedescriptions: str | None
    tokenlength: int
    alloweditaftercompletion: YesNo
    googleanalyticsstyle: str | None
    googleanalyticsapikey: str | None
    tokenencryptionoptions: str

    showxquestions: YesNo
    showgroupinfo: YesNo
    shownoanswer: YesNo
    showqnumcode: YesNo
    showwelcome: YesNo
    showprogress: YesNo
    questionindex: int
    navigationdelay: int
    nokeyboard: YesNo

    bouncetime: int | None
    bounceprocessing: YesNo
    bounceaccounttype: str | None
    bounceaccounthost: str | None
    bounceaccountpass: str | None
    bounceaccountencryption: str | None
    bounceaccountuser: str | None

    htmlemail: YesNo
    sendconfirmation: YesNo
    bounce_email: str
    emailresponseto: str | None
    emailnotificationto: str | None

    admin: str
    admin_email: str

    language: str
    additional_languages: str


class CPDBParticipantImportResult(t.TypedDict):
    """CPDB participant import result."""

    ImportCount: int
    UpdateCount: int


class SurveyUserActivationSettings(t.TypedDict, total=False):
    """User settings for survey activation."""

    anonymized: bool
    datestamp: bool
    ipaddr: bool
    ipanonymize: bool
    refurl: bool
    savetimings: bool
