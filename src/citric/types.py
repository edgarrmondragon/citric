"""Citric Python types."""

from __future__ import annotations

import sys
import typing as t

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict  # noqa: ICN003
else:
    from typing_extensions import Literal, TypedDict

if sys.version_info >= (3, 10):
    from typing import TypeAlias  # noqa: ICN003
else:
    from typing_extensions import TypeAlias

if t.TYPE_CHECKING:
    from citric import enums

Result: TypeAlias = t.Any
YesNo: TypeAlias = Literal["Y", "N"]


class FileUploadResult(TypedDict):
    """File upload result.

    Keys:
        success: Whether the file was uploaded successfully.
        size: The size of the file.
        name: The name of the file.
        ext: The extension of the file.
        filename: The filename of the file.
        msg: The message of the file.
    """

    success: bool
    size: int
    name: str
    ext: str
    filename: str
    msg: str


class GroupProperties(TypedDict, total=False):
    """Group properties.

    Keys:
        gid: The group ID.
        sid: The survey ID.
        group_order: The group order.
        randomization_group: The randomization group.
        grelevance: The group relevance.
        group_name: The group name.
        description: The group description.
    """

    gid: int
    sid: int
    group_order: int
    randomization_group: str
    grelevance: str
    group_name: str
    description: str


class LanguageProperties(TypedDict, total=False):
    """Language properties.

    Keys:
        surveyls_survey_id: The survey ID.
        surveyls_language: The language code.
        surveyls_title: The survey title.
        surveyls_description: The survey description.
        surveyls_welcometext: The survey welcome text.
        surveyls_endtext: The survey end text.

        surveyls_policy_notice: The survey policy notice.
        surveyls_policy_error: The survey policy error.
        surveyls_policy_notice_label: The survey policy notice label.

        surveyls_url: The survey URL.
        surveyls_urldescription: The survey URL description.

        surveyls_email_invite_subj: The survey email invite subject.
        surveyls_email_invite: The survey email invite.
        surveyls_email_remind_subj: The survey email remind subject.
        surveyls_email_remind: The survey email remind.
        surveyls_email_register_subj: The survey email register subject.
        surveyls_email_register: The survey email register.
        surveyls_email_confirm_subj: The survey email confirm subject.
        surveyls_email_confirm: The survey email confirm.

        surveyls_dateformat: The survey date format.
        surveyls_numberformat: The survey number format.
        surveyls_attributecaptions: The survey attribute captions.

        email_admin_notification_subj: The email admin notification subject.
        email_admin_notification: The email admin notification.
        email_admin_responses_subj: The email admin responses subject.
        email_admin_responses: The email admin responses.

        attachments: The attachments.
    """

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


class OperationStatus(TypedDict):
    """Delete language result.

    Keys:
        status: The status of the operation.
    """

    status: str


class QuestionsListElement(TypedDict):
    """List questions result.

    Keys:
        id: The question ID.
        qid: The question ID.
        parent_qid: The parent question ID.
        gid: The group ID.
        sid: The survey ID.

        question: The question.
        help: The question help text.
        language: The question language.

        type: The question type.
        title: The question title.
        preg: The question preg.
        other: Whether the question has an "other" option.
        mandatory: Whether the question is mandatory.
        encrypted: Whether the question is encrypted.
        question_order: The question order.
        scale_id: The question scale ID.
        same_default: The question same default.
        relevance: The question relevance.
        question_theme_name: The question theme name.
        modulename: The question module name.
        same_script: The question same script.
    """

    id: int  # noqa: A003
    qid: int
    parent_qid: int
    gid: int
    sid: int

    question: str
    help: str  # noqa: A003
    language: str

    type: str  # noqa: A003
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


class QuestionProperties(TypedDict, total=False):
    """Question properties result.

    Keys:
        id: The question ID.
        qid: The question ID.
        parent_qid: The parent question ID.
        gid: The group ID.
        sid: The survey ID.

        type: The question type.
        title: The question title.
        preg: The question preg.
        other: Whether the question has an "other" option.
        mandatory: Whether the question is mandatory.
        encrypted: Whether the question is encrypted.
        question_order: The question order.
        scale_id: The question scale ID.
        same_default: The question same default.
        relevance: The question relevance.
        question_theme_name: The question theme name.
        modulename: The question module name.
        same_script: The question same script.

        available_answers: The available answers.
        answer_options: The answer options.
        subquestions: The subquestions.
        default_values: The default values.

        attributes: The question attributes.
        attributes_lang: The question attributes language.
    """

    qid: int
    parent_qid: int
    gid: int
    sid: int

    type: str  # noqa: A003
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


class QuotaListElement(TypedDict):
    """List quotas result.

    Keys:
        id: The quota ID.
        name: The quota name.
        qlimit: The quota limit.
        active: Whether the quota is active.
        action: The quota action.
        autoload_url: Whether the quota autoload URL is active.
    """

    id: int  # noqa: A003
    name: str
    action: int
    limit: int
    active: int
    autoload_url: int


class QuotaProperties(TypedDict, total=False):
    """Quota properties result.

    Keys:
        id: The quota ID.
        sid: The survey ID.
        name: The quota name.
        qlimit: The quota limit.
        action: The quota action.
        active: Whether the quota is active.
        autoload_url: Whether the quota autoload URL is active.
    """

    id: int  # noqa: A003
    sid: int
    name: str
    qlimit: int
    action: int
    active: int
    autoload_url: int


class RPCResponse(TypedDict):
    """RPC response payload.

    Keys:
        id: The ID of the request.
        result: The result of the RPC call.
        error: The error message of the RPC call.
    """

    id: int  # noqa: A003
    result: Result
    error: str | None


class SetQuotaPropertiesResult(TypedDict):
    """Set quota properties result.

    Keys:
        success: Whether the operation was successful.
        message: The quota properties.
    """

    success: bool
    message: QuotaProperties


class SurveyProperties(TypedDict, total=False):
    """Survey properties result.

    Keys:
        sid: The survey ID.
        owner_id: The survey owner ID.
        gsid: The survey group ID.
        active: Whether the survey is active.
        expires: The survey expiration date.
        startdate: The survey start date.
        anonymized: Whether the survey is anonymized.
        faxto: The survey fax number.
        format: The survey format.
        savetiming: Whether the survey saves timing.
        template: The survey template.
        datesstamp: Whether the survey stamps dates.
        usecookie: Whether the survey uses cookies.
        allowregister: Whether the survey allows registration.
        allowsave: Whether the survey allows saving.
        autonumber_start: The survey autonumber start.
        autoredirect: Whether the survey auto-redirects.
        allowprev: Whether the survey allows previous.
        printanswers: Whether the survey prints answers.
        ipaddr: Whether the survey uses IP addresses.
        ipanonymize: Whether the survey anonymizes IP addresses.
        refurl: Whether the survey uses referrer URLs.
        datecreated: The survey creation date.
        showsurveypolicynotice: Whether the survey shows policy notice.
        publicstatistics: Whether the survey is public.
        publicgraphs: Whether the survey graphs are public.
        listpublic: Whether the survey is listed publicly.
        tokenanswerspersistence: Whether the survey token answers persist.
        assessments: Whether the survey uses assessments.
        usecaptcha: Whether the survey uses CAPTCHA.
        usetokens: Whether the survey uses tokens.
        attributedescriptions: The survey attribute descriptions.
        tokenlength: The survey token length.
        alloweditaftercompletion: Whether the survey allows editing after completion.
        googleanalyticsstyle: Whether the survey uses Google Analytics style.
        googleanalyticsapikey: The survey Google Analytics API key.
        tokenencryptionoptions: The survey token encryption options.

        showxquestions: Whether the survey shows x questions.
        showgroupinfo: Whether the survey shows group info.
        shownoanswer: Whether the survey shows no answer.
        showqnumcode: Whether the survey shows question number code.
        showwelcome: Whether the survey shows welcome.
        showprogress: Whether the survey shows progress.
        questionindex: Index of the survey question.
        navigationdelay: The survey navigation delay.
        nokeyboard: Whether the survey should allow keyboard input.

        bouncetime: The survey bounce time.
        bounceprocessing: Whether the survey bounces are processed.
        bounceaccounttype: The survey bounce account type.
        bounceaccounthost: The survey bounce account host.
        bounceaccountpass: The survey bounce account password.
        bounceaccountencryption: The survey bounce account encryption.
        bounceaccountuser: The survey bounce account user.

        htmlemail: Whether the survey emails are HTML.
        sendconfirmation: Whether the survey sends confirmation.
        bounce_email: The survey bounce email.
        emailresponseto: The survey email response to.
        emailnotificationto: The survey email notification to.

        admin: The survey admin.
        admin_email: The survey admin email.

        language: The survey language.
        additional_languages: The survey additional languages.
    """

    sid: int
    owner_id: int
    gsid: int
    active: YesNo
    expires: str | None
    startdate: str | None
    anonymized: YesNo
    faxto: str
    format: enums.NewSurveyType  # noqa: A003
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


class CPDBParticipantImportResult(TypedDict):
    """CPDB participant import result.

    Keys:
        ImportCount: The number of participants imported.
        UpdateCount: The number of participants updated.
    """

    ImportCount: int
    UpdateCount: int
