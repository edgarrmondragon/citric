"""Citric Python types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict

if TYPE_CHECKING:
    import io
    import sys

    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

    from citric import enums

__all__ = [
    "CPDBParticipantImportResult",
    "EncodedFile",
    "ExporAdditionalOptions",
    "FileMetadata",
    "FileUploadResult",
    "GroupProperties",
    "LanguageProperties",
    "OperationStatus",
    "Permission",
    "QuestionProperties",
    "QuestionReference",
    "QuestionsListElement",
    "QuotaListElement",
    "QuotaProperties",
    "RPCResponse",
    "ReadableFile",
    "Result",
    "SetQuotaPropertiesResult",
    "SurveyListElement",
    "SurveyProperties",
    "SurveyUserActivationSettings",
    "UserDetails",
]

Result: TypeAlias = Any

#: Yes/No/Inherit type alias.
YesNo: TypeAlias = Literal["Y", "N", "I"]


class FileUploadResult(TypedDict):
    """File upload result."""

    success: bool
    """Whether the file was uploaded successfully."""

    size: int
    """The size of the file."""

    name: str
    """The name of the file."""

    ext: str
    """The extension of the file."""

    filename: str
    """The filename of the file."""

    msg: str
    """The message of the file."""


class GroupProperties(TypedDict, total=False):
    """Group properties."""

    gid: int
    """The group ID."""

    sid: int
    """The survey ID."""

    group_order: int
    """The group order."""

    randomization_group: str
    """The randomization group."""

    grelevance: str
    """The group relevance."""

    group_name: str
    """The group name."""

    description: str
    """The group description."""


class LanguageProperties(TypedDict, total=False):
    """Language properties."""

    surveyls_survey_id: int
    """The survey ID."""

    surveyls_language: str
    """The language code."""

    surveyls_title: str
    """The survey title."""

    surveyls_description: str | None
    """The survey description."""

    surveyls_welcometext: str | None
    """The survey welcome text."""

    surveyls_endtext: str | None
    """The survey end text."""

    surveyls_policy_notice: str | None
    """The survey policy notice."""

    surveyls_policy_error: str | None
    """The survey policy error."""

    surveyls_policy_notice_label: str | None
    """The survey policy notice label."""

    surveyls_url: str
    """The survey URL."""

    surveyls_urldescription: str | None
    """The survey URL description."""

    surveyls_alias: str | None
    """The survey alias."""

    surveyls_email_invite_subj: str
    """The survey email invite subject."""

    surveyls_email_invite: str
    """The survey email invite."""

    surveyls_email_remind_subj: str
    """The survey email remind subject."""

    surveyls_email_remind: str
    """The survey email remind."""

    surveyls_email_register_subj: str
    """The survey email register subject."""

    surveyls_email_register: str
    """The survey email register."""

    surveyls_email_confirm_subj: str
    """The survey email confirm subject."""

    surveyls_email_confirm: str
    """The survey email confirm."""

    surveyls_dateformat: int
    """The survey date format."""

    surveyls_numberformat: int
    """The survey number format."""

    surveyls_attributecaptions: str | None
    """The survey attribute captions."""

    email_admin_notification_subj: str
    """The email admin notification subject."""

    email_admin_notification: str
    """The email admin notification."""

    email_admin_responses_subj: str
    """The email admin responses subject."""

    email_admin_responses: str
    """The email admin responses."""

    attachments: str | None
    """The attachments."""


class OperationStatus(TypedDict):
    """Delete language result."""

    status: str
    """The status of the operation."""


class QuestionsListElement(TypedDict):
    """List questions result."""

    id: int
    """The question ID."""
    qid: int
    """The question ID."""
    parent_qid: int
    """The parent question ID."""
    gid: int
    """The group ID."""
    sid: int
    """The survey ID."""

    question: str
    """The question."""
    help: str
    """The question help text."""
    language: str
    """The question language."""

    type: str
    """The question type."""

    title: str
    """The question title."""

    preg: str
    """The question preg."""

    other: YesNo
    """Whether the question has an "other" option."""

    mandatory: YesNo
    """Whether the question is mandatory."""

    encrypted: YesNo
    """Whether the question is encrypted."""

    question_order: int
    """The question order."""

    scale_id: int
    """The question scale ID."""

    same_default: int
    """The question same default."""

    relevance: str
    """The question relevance."""

    question_theme_name: str
    """The question theme name."""

    modulename: str
    """The question module name."""

    same_script: int
    """The question same script."""


class QuestionProperties(TypedDict, total=False):
    """Question properties result."""

    qid: int
    """The question ID."""

    parent_qid: int
    """The parent question ID."""

    gid: int
    """The group ID."""

    sid: int
    """The survey ID."""

    question: str
    """The question text in the survey language."""

    help: str
    """The question help text in the survey language."""

    script: str
    """The question script."""

    questionl10ns: dict[str, Any]
    """The question language-specific attributes."""

    type: str
    """The question type."""

    title: str
    """The question title."""

    preg: str
    """The question preg."""

    other: YesNo
    """Whether the question has an "other" option."""

    mandatory: YesNo
    """Whether the question is mandatory."""

    encrypted: YesNo
    """Whether the question is encrypted."""

    question_order: int
    """The question order."""

    scale_id: int
    """The question scale ID."""

    same_default: int
    """The question same default."""

    relevance: str
    """The question relevance."""

    question_theme_name: str
    """The question theme name."""

    modulename: str
    """The question module name."""

    same_script: int
    """The question same script."""

    available_answers: Any
    """The available answers."""

    answer_options: Any
    """The answer options."""

    subquestions: Any
    """The subquestions."""

    default_values: Any
    """The default values."""

    attributes: dict[str, Any]
    """The question attributes."""

    attributes_lang: dict[str, Any]
    """The question attributes language."""


class QuotaListElement(TypedDict):
    """List quotas result."""

    id: int
    """The quota ID."""

    name: str
    """The quota name."""

    action: int
    """The quota limit."""

    limit: int
    """Whether the quota is active."""

    active: int
    """The quota action."""

    autoload_url: int
    """Whether the quota autoload URL is active."""


class QuotaProperties(TypedDict, total=False):
    """Quota properties result."""

    id: int
    """The quota ID."""

    sid: int
    """The survey ID."""

    name: str
    """The quota name."""

    qlimit: int
    """The quota limit."""

    action: int
    """The quota action."""

    active: int
    """Whether the quota is active."""

    autoload_url: int
    """Whether the quota autoload URL is active."""

    completeCount: int
    """Count of completed interviews for this quota."""

    # Quota Language Settings

    quotals_message: str
    """Quota message for this language."""

    quotals_url: str
    """Quota end-URL for this language."""

    quotals_urldescrip: str
    """Quota end-URL description for this language."""


class RPCResponse(TypedDict):
    """RPC response payload."""

    id: int
    """The ID of the request."""

    result: Result
    """The result of the RPC call."""

    error: str | None
    """The error message of the RPC call."""


class SetQuotaPropertiesResult(TypedDict):
    """Set quota properties result."""

    success: bool
    """Whether the operation was successful."""

    message: QuotaProperties
    """The quota properties."""


class SurveyListElement(TypedDict, total=False):
    """List surveys result."""

    sid: int
    """The survey ID."""

    gsid: int
    """The survey group ID.

    .. minlimesurveyattribute:: 6.10.0
    """

    surveyls_title: str
    """The survey title."""

    startdate: str
    """The survey start date."""

    expires: str
    """The survey expiration date."""

    active: YesNo
    """Whether the survey is active."""


class SurveyProperties(TypedDict, total=False):
    """Survey properties result."""

    sid: int
    """The survey ID."""

    owner_id: int
    """The survey owner ID."""

    gsid: int
    """The survey group ID."""

    active: YesNo
    """Whether the survey is active."""

    expires: str | None
    """The survey expiration date."""

    startdate: str | None
    """The survey start date."""

    anonymized: YesNo
    """Whether the survey is anonymized."""

    faxto: str
    """The survey fax number."""

    format: enums.NewSurveyType
    """The survey format."""

    savetiming: YesNo
    """Whether the survey saves timing."""

    template: str
    """The survey template."""

    datesstamp: YesNo
    """Whether the survey stamps dates."""

    usecookie: YesNo
    """Whether the survey uses cookies."""

    allowregister: YesNo
    """Whether the survey allows registration."""

    allowsave: YesNo
    """Whether the survey allows saving."""

    autonumber_start: int
    """The survey autonumber start."""

    autoredirect: YesNo
    """Whether the survey auto-redirects."""

    allowprev: YesNo
    """Whether the survey allows previous."""

    printanswers: YesNo
    """Whether the survey prints answers."""

    ipaddr: YesNo
    """Whether the survey uses IP addresses."""

    ipanonymize: YesNo
    """Whether the survey anonymizes IP addresses."""

    refurl: YesNo
    """Whether the survey uses referrer URLs."""

    datecreated: str
    """The survey creation date."""

    showsurveypolicynotice: YesNo
    """Whether the survey shows policy notice."""

    publicstatistics: YesNo
    """Whether the survey is public."""

    publicgraphs: YesNo
    """Whether the survey graphs are public."""

    listpublic: YesNo
    """Whether the survey is listed publicly."""

    tokenanswerspersistence: YesNo
    """Whether the survey token answers persist."""

    assessments: YesNo
    """Whether the survey uses assessments."""

    usecaptcha: YesNo
    """Whether the survey uses CAPTCHA."""

    usetokens: YesNo
    """Whether the survey uses tokens."""

    attributedescriptions: str | None
    """The survey attribute descriptions."""

    tokenlength: int
    """The survey token length."""

    alloweditaftercompletion: YesNo
    """Whether the survey allows editing after completion."""

    googleanalyticsstyle: str | None
    """Whether the survey uses Google Analytics style."""

    googleanalyticsapikey: str | None
    """The survey Google Analytics API key."""

    tokenencryptionoptions: str
    """The survey token encryption options."""

    showxquestions: YesNo
    """Whether the survey shows x questions."""

    showgroupinfo: YesNo
    """Whether the survey shows group info."""

    shownoanswer: YesNo
    """Whether the survey shows no answer."""

    showqnumcode: YesNo
    """Whether the survey shows question number code."""

    showwelcome: YesNo
    """Whether the survey shows welcome."""

    showprogress: YesNo
    """Whether the survey shows progress."""

    questionindex: int
    """Index of the survey question."""

    navigationdelay: int
    """The survey navigation delay."""

    nokeyboard: YesNo
    """Whether the survey should allow keyboard input."""

    bouncetime: int | None
    """The survey bounce time."""

    bounceprocessing: YesNo
    """Whether the survey bounces are processed."""

    bounceaccounttype: str | None
    """The survey bounce account type."""

    bounceaccounthost: str | None
    """The survey bounce account host."""

    bounceaccountpass: str | None
    """The survey bounce account password."""

    bounceaccountencryption: str | None
    """The survey bounce account encryption."""

    bounceaccountuser: str | None
    """The survey bounce account user."""

    htmlemail: YesNo
    """Whether the survey emails are HTML."""

    sendconfirmation: YesNo
    """Whether the survey sends confirmation."""

    bounce_email: str
    """The survey bounce email."""

    emailresponseto: str | None
    """The survey email response to."""

    emailnotificationto: str | None
    """The survey email notification to."""

    admin: str
    """The survey admin."""

    admin_email: str
    """The survey admin email."""

    language: str
    """The survey language."""

    additional_languages: str
    """The survey additional languages."""


class CPDBParticipantImportResult(TypedDict):
    """CPDB participant import result."""

    ImportCount: int
    """The number of participants imported."""

    UpdateCount: int
    """The number of participants updated."""


class SurveyUserActivationSettings(TypedDict, total=False):
    """User settings for survey activation."""

    anonymized: bool
    """Whether the survey is anonymized."""

    datestamp: bool
    """Whether the survey records dates."""

    ipaddr: bool
    """Whether the survey records IP addresses."""

    ipanonymize: bool
    """Whether the survey anonymizes IP addresses."""

    refurl: bool
    """Whether the survey records referrer URLs."""

    savetimings: bool
    """Whether the survey saves response timings."""


class ExporAdditionalOptions(TypedDict, total=False):
    """Export formatting options."""

    convertY: bool
    """Convert ``Y`` response values.

    If ``response_type`` is ``short``, then this indicates that ``Y`` responses should
    be converted to another value that is specified by ``yValue``.
    """

    yValue: Any
    """The value to convert ``Y`` responses to."""

    convertN: bool
    """Convert ``N`` response values.

    If ``response_type`` is ``short``, then this indicates that ``N`` responses should
    be converted to another value that is specified by ``nValue``.
    """

    nValue: Any
    """The value to convert ``N`` responses to."""

    headerSpacesToUnderscores: bool
    """Indicates whether to convert spaces in question headers to underscores."""

    headingTextLength: int
    """Indicates whether to ellipsize each text part to."""

    useEMCode: bool
    """Indicates whether to use ExpressionScript Engine code."""

    headCodeTextSeparator: str
    """What is the characters to separate code and text."""

    csvFieldSeparator: str
    """What is the character to separate CSV fields."""

    csvMaskEquations: bool
    """Mask CSV/Excel equation fields to prevent CSV injection attacks."""

    stripHtmlCode: Literal["1", "0"]
    """Strip HTML code from the responses.

    - ``1``: Strip HTML code.
    - ``0``: No stripping.
    """


class Permission(TypedDict, total=False):
    """Permission."""

    id: int
    """The permission ID."""

    entity: str
    """The permission entity."""

    entity_id: int
    """The permission entity ID."""

    permission: str
    """The permission."""

    create_p: int
    """Whether the permission can create."""

    read_p: int
    """Whether the permission can read."""

    update_p: int
    """Whether the permission can update."""


class UserDetails(TypedDict, total=False):
    """User details."""

    uid: int
    """The user ID."""

    users_name: str
    """The user name."""

    full_name: str
    """The user full name."""

    parent_id: int
    """The user parent ID."""

    lang: str
    """The user preferred language."""

    email: str
    """The user email."""

    htmleditormode: str
    """The user preferred HTML editor mode."""

    templateeditormode: str
    """The user preferred template editor mode."""

    questionselectormode: str
    """The user preferred question type selector."""

    one_time_pw: str
    """The user one-time password."""

    dateformat: int
    """The user date format."""

    created: str
    """The user creation date."""

    modified: str
    """The user modification date."""

    validation_key: str
    """The user validation key."""

    validation_key_expiration: str
    """The user validation key expiration."""

    last_forgot_email_password: str
    """The user last forgot email password."""

    permissions: list[Permission]
    """The user permissions."""

    last_login: str
    """The user last login."""

    user_status: enums.UserStatus
    """The user status."""


class QuestionReference(TypedDict):
    """Uploaded file question reference."""

    title: str
    """Question title."""

    qid: int
    """Question ID."""


class FileMetadata(FileUploadResult):
    """Uploaded file metadata."""

    question: QuestionReference
    """:class:`~citric.client.QuestionReference` object."""

    index: int
    """File index."""


class EncodedFile(TypedDict):
    """A file uploaded to a survey response."""

    meta: FileMetadata
    """:class:`~citric.client.FileMetadata` object."""

    content: str
    """File content as base64 encoded string."""


class ReadableFile(TypedDict):
    """A file uploaded to a survey response."""

    meta: FileMetadata
    """:class:`~citric.client.FileMetadata` object."""

    content: io.BytesIO
    """File content as :py:class:`io.BytesIO <io.BytesIO>`."""
