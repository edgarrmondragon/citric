"""Python API Client."""

from __future__ import annotations

import base64
import datetime
import io
import re
import typing as t
from dataclasses import dataclass
from pathlib import Path

import requests

from citric import enums
from citric._compat import future_parameter
from citric.exceptions import LimeSurveyStatusError
from citric.session import Session

if t.TYPE_CHECKING:
    import sys
    from os import PathLike
    from types import TracebackType

    from citric import types
    from citric.objects import Participant

    if sys.version_info >= (3, 11):
        from typing import Self, Unpack  # noqa: ICN003
    else:
        from typing_extensions import Self, Unpack

__all__ = [
    "Client",
    "FileMetadata",
    "QuestionReference",
    "UploadedFile",
]

EMAILS_SENT_STATUS_PATTERN = re.compile(r"(-?\d+) left to send")


@dataclass
class QuestionReference:
    """Uploaded file question reference."""

    title: str
    """Question title."""

    qid: int
    """Question ID."""


@dataclass
class FileMetadata:
    """Uploaded file metadata."""

    title: str
    """File title."""

    comment: str
    """File comment."""

    name: str
    """File name."""

    filename: str
    """LimeSurvey internal file name."""

    size: float
    """File size in bytes."""

    ext: str
    """File extension."""

    question: QuestionReference
    """:class:`~citric.client.QuestionReference` object."""

    index: int
    """File index."""


@dataclass
class UploadedFile:
    """A file uploaded to a survey response."""

    meta: FileMetadata
    """:class:`~citric.client.FileMetadata` object."""

    content: io.BytesIO
    """File content as :py:class:`io.BytesIO <io.BytesIO>`.
    """


class Client:  # noqa: PLR0904
    """LimeSurvey Remote Control client.

    Offers explicit wrappers for RPC methods and simplifies common workflows.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A :py:class:`requests.Session <requests.Session>` object.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).

    .. versionadded:: 0.0.6
       Support Auth plugins with the ``auth_plugin`` parameter.
    """

    session_class = Session

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: requests.Session | None = None,
        auth_plugin: str = "Authdb",
    ) -> None:
        self.__session = self.session_class(
            url,
            username,
            password,
            requests_session=requests_session or requests.session(),
            auth_plugin=auth_plugin,
        )

    def close(self) -> None:
        """Close client session."""
        self.session.close()

    def __enter__(self: Self) -> Self:
        """Create client context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Safely exit the client context."""
        self.close()

    @property
    def session(self) -> Session:
        """Low-level RPC session."""
        return self.__session

    def get_fieldmap(self, survey_id: int) -> dict[str, t.Any]:
        """Get fieldmap for a survey.

        Calls :rpc_method:`get_fieldmap`.

        Args:
            survey_id: ID of survey to get fieldmap for.

        Returns:
            Dictionary mapping response keys to LimeSurvey internal representation.

        .. versionadded:: 0.3.0
        """
        return self.session.get_fieldmap(survey_id)

    def activate_survey(
        self,
        survey_id: int,
        *,
        user_activation_settings: types.SurveyUserActivationSettings | None = None,
    ) -> types.OperationStatus:
        """Activate a survey.

        Calls :rpc_method:`activate_survey`.

        Args:
            survey_id: ID of survey to be activated.
            user_activation_settings: Optional user activation settings.

        Returns:
            Status and plugin feedback.

        .. versionadded:: 0.0.1
        .. versionchanged:: 0.10.0
           The ``user_activation_settings`` optional parameter was added.
        """
        activation_settings = (
            {
                key: "Y" if value else "N"
                for key, value in user_activation_settings.items()
            }
            if user_activation_settings
            else None
        )
        return self.session.activate_survey(survey_id, activation_settings)

    def activate_tokens(
        self,
        survey_id: int,
        attributes: list[int] | None = None,
    ) -> types.OperationStatus:
        """Initialise the survey participant table.

        New participant tokens may be later added.

        Calls :rpc_method:`activate_tokens`.

        Args:
            survey_id: ID of survey to be activated.
            attributes: Optional list of participant attributes numbers to be activated.

        Returns:
            Status message.

        .. versionadded:: 0.0.1
        """
        return self.session.activate_tokens(survey_id, attributes or [])

    def add_language(self, survey_id: int, language: str) -> types.OperationStatus:
        """Add a survey language.

        Calls :rpc_method:`add_language`.

        Args:
            survey_id: ID of the Survey for which a language will be added.
            language: A valid language shortcut to add to the current Survey. If the
                language already exists no error will be given.

        Returns:
            Status message.

        .. versionadded:: 0.0.10
        """
        return self.session.add_language(survey_id, language)

    def add_participants(
        self,
        survey_id: int,
        *,
        participant_data: t.Sequence[t.Mapping[str, t.Any]],
        create_tokens: bool = True,
    ) -> list[dict[str, t.Any]]:
        """Add participants to a survey.

        Calls :rpc_method:`add_participants`.

        Args:
            survey_id: Survey to add participants to.
            participant_data: Information to create participants with.
            create_tokens: Whether to create the participants with tokens.

        Returns:
            Information of newly created participants.

        .. versionadded:: 0.0.1
        .. versionchanged:: 0.4.0
           Use keyword-only arguments.
        """
        return self.session.add_participants(
            survey_id,
            participant_data,
            create_tokens,
        )

    def add_quota(
        self,
        survey_id: int,
        name: str,
        limit: int,
        *,
        active: bool = True,
        action: str = enums.QuotaAction.TERMINATE,
        autoload_url: bool = False,
        message: str = "",
        url: str = "",
        url_description: str = "",
    ) -> int:
        """Add a quota to a LimeSurvey survey.

        Calls :rpc_method:`add_quota`.

        Args:
            survey_id: ID of the survey to add the quota to.
            name: Name of the quota.
            limit: Limit of the quota.
            active: Whether the quota is active.
            action: Action to take when the limit is reached.
            autoload_url: Whether to automatically load the URL.
            message: Message to display to the respondent when the limit is reached.
            url: URL to redirect the respondent to when the limit is reached.
            url_description: Description of the URL.

        Returns:
            ID of the newly created quota.

        .. versionadded:: 0.6.0
        .. minlimesurvey:: 6.0.0
        """
        return self.session.add_quota(
            survey_id,
            name,
            limit,
            active,
            enums.QuotaAction(action),
            autoload_url,
            message,
            url,
            url_description,
        )

    def add_survey(
        self,
        survey_id: int,
        title: str,
        language: str,
        survey_format: str | enums.NewSurveyType = "G",
    ) -> int:
        """Add a new empty survey.

        Calls :rpc_method:`add_survey`.

        Args:
            survey_id: The desired ID of the Survey to add.
            title: Title of the new Survey.
            language: Default language of the Survey.
            survey_format: Question appearance format (A, G or S) for "All on one page",
                "Group by Group", "Single questions", default to group by group (G).

        Returns:
            The new survey ID.

        .. versionadded:: 0.0.10
        """
        return self.session.add_survey(
            survey_id,
            title,
            language,
            enums.NewSurveyType(survey_format),
        )

    def delete_participants(
        self,
        survey_id: int,
        participant_ids: t.Sequence[int],
    ) -> list[dict[str, t.Any]]:
        """Add participants to a survey.

        Calls :rpc_method:`delete_participants`.

        Args:
            survey_id: Survey to delete participants to.
            participant_ids: Participant IDs to be deleted.

        Returns:
            Information of removed participants.

        .. versionadded:: 0.0.1
        """
        return self.session.delete_participants(
            survey_id,
            participant_ids,
        )

    def _get_question_mapping(
        self,
        survey_id: int,
    ) -> dict[str, types.QuestionsListElement]:
        """Get question mapping.

        Args:
            survey_id: Survey ID.

        Returns:
            Question mapping.
        """
        return {q["title"]: q for q in self.list_questions(survey_id)}

    @staticmethod
    def _map_response_keys(
        response_data: t.Mapping[str, t.Any],
        question_mapping: dict[str, types.QuestionsListElement],
    ) -> dict[str, t.Any]:
        """Convert response keys to LimeSurvey's internal representation.

        Args:
            response_data: The response mapping.
            question_mapping: A mapping of question titles to question dictionaries.

        Returns:
            A new dictionary with the keys mapped to the <SID>X<GID>X<QID> format.

        >>> keys = {"Q1": "foo", "Q2": "bar", "BAZ": "qux"}
        >>> q1 = {"title": "Q1", "qid": 9, "gid": 7, "sid": 123}
        >>> q2 = {"title": "Q2", "qid": 10, "gid": 7, "sid": 123}
        >>> questions = {"Q1": q1, "Q2": q2}
        >>> mapped_keys = Client._map_response_keys(keys, questions)
        >>> mapped_keys
        {'123X7X9': 'foo', '123X7X10': 'bar', 'BAZ': 'qux'}
        """
        return {
            (
                "{sid}X{gid}X{qid}".format(**question_mapping[key])
                if key in question_mapping
                else key
            ): value
            for key, value in response_data.items()
        }

    def add_group(self, survey_id: int, title: str, description: str = "") -> int:
        """Add a new empty question group to a survey.

        Calls :rpc_method:`add_group`.

        Args:
            survey_id: ID of the Survey to add the group.
            title: Name of the group.
            description: Optional description of the group.

        Returns:
            The id of the new group.

        .. versionadded:: 0.0.8
        """
        return self.session.add_group(survey_id, title, description)

    def _add_response(
        self,
        survey_id: int,
        response_data: t.Mapping[str, t.Any],
    ) -> int:
        """Add a single response to a survey.

        Args:
            survey_id: Survey to add the response to.
            response_data: Single response as a mapping from question codes of the form
                <SID>X<GID>X<QID> to response values.

        Returns:
            ID of the new response.
        """
        return int(self.session.add_response(survey_id, response_data))

    def add_response(self, survey_id: int, response_data: t.Mapping[str, t.Any]) -> int:
        """Add a single response to a survey.

        Args:
            survey_id: Survey to add the response to.
            response_data: Single response as a mapping.

        Returns:
            ID of the new response.

        .. versionadded:: 0.0.1
        """
        # Transform question codes to the format LimeSurvey expects
        questions = self._get_question_mapping(survey_id)
        data = self._map_response_keys(response_data, questions)
        return self._add_response(survey_id, data)

    def add_responses(
        self,
        survey_id: int,
        responses: t.Iterable[t.Mapping[str, t.Any]],
    ) -> list[int]:
        """Add multiple responses to a survey.

        Args:
            survey_id: Survey to add the response to.
            responses: Iterable of survey responses.

        Returns:
            IDs of the new responses.

        .. versionadded:: 0.0.1
        """
        ids = []
        questions = self._get_question_mapping(survey_id)
        for response in responses:
            data = self._map_response_keys(response, questions)
            response_id = self._add_response(survey_id, data)
            ids.append(response_id)
        return ids

    def update_response(self, survey_id: int, response_data: dict[str, t.Any]) -> bool:
        """Update a response.

        Calls :rpc_method:`update_response`.

        Args:
            survey_id: Survey to update the response in.
            response_data: Response data to update.

        Returns:
            True if the response was updated, False otherwise.

        .. versionadded:: 0.2.0
        """
        questions = self._get_question_mapping(survey_id)
        data = self._map_response_keys(response_data, questions)
        return self.session.update_response(survey_id, data)

    @future_parameter("6.4.0", "destination_survey_id")
    def copy_survey(
        self,
        survey_id: int,
        name: str,
        *,
        destination_survey_id: int | None = None,
    ) -> dict[str, t.Any]:
        """Copy a survey.

        Calls :rpc_method:`copy_survey`.

        Args:
            survey_id: ID of the source survey.
            name: Name of the new survey.
            destination_survey_id: ID of the new survey. If already used a, random one
                will be generated.

        Returns:
            Dictionary of status message and the new survey ID.

        .. versionadded:: 0.0.10
        .. versionchanged:: 0.10.0
           The ``destination_survey_id`` optional parameter was added.
        .. futureparam:: 6.4.0 destination_survey_id
        """
        return self.session.copy_survey(survey_id, name, destination_survey_id)

    def import_cpdb_participants(
        self,
        participants: t.Sequence[Participant],
        *,
        update: bool = False,
    ) -> types.CPDBParticipantImportResult:
        """Import CPDB participants.

        Calls :rpc_method:`cpd_importParticipants`.

        Args:
            participants: CPDB participant data.
            update: Whether to update existing participants.

        Returns:
            IDs of the new participants.

        .. versionadded:: 0.7.0
        """
        return self.session.cpd_importParticipants(
            [participant.to_dict() for participant in participants],
            update,
        )

    def delete_group(self, survey_id: int, group_id: int) -> int:
        """Delete a group.

        Args:
            survey_id: ID of the Survey that the group belongs to.
            group_id: ID of the group to delete.

        Returns:
            ID of the deleted group.

        .. versionadded:: 0.0.10
        """
        return self.session.delete_group(survey_id, group_id)

    def delete_language(self, survey_id: int, language: str) -> types.OperationStatus:
        """Delete a language from a survey.

        Args:
            survey_id: ID of the Survey for which a language will be deleted from.
            language: Language to delete.

        Returns:
            Status message.

        .. versionadded:: 0.0.12
        .. minlimesurvey:: 5.3.4
        """
        return self.session.delete_language(survey_id, language)

    def delete_quota(self, quota_id: int) -> types.OperationStatus:
        """Delete a LimeSurvey quota.

        Calls :rpc_method:`delete_quota`.

        Args:
            quota_id: ID of the quota to delete.

        Returns:
            True if the quota was deleted.

        .. versionadded:: 0.6.0
        .. minlimesurvey:: 6.0.0
        """
        return self.session.delete_quota(quota_id)

    def delete_response(
        self,
        survey_id: int,
        response_id: int,
    ) -> types.OperationStatus:
        """Delete a response in a survey.

        Args:
            survey_id: ID of the survey the response belongs to.
            response_id: ID of the response to delete.

        Returns:
            Status message.

        .. versionadded:: 0.0.2
        """
        return self.session.delete_response(survey_id, response_id)

    def delete_question(self, question_id: int) -> int:
        """Delete a survey.

        Calls :rpc_method:`delete_question`.

        Args:
            question_id: ID of Question to delete.

        Returns:
            ID of the deleted question.

        .. versionadded:: 0.1.0
        .. minlimesurvey:: 5.3.19
        """
        return self.session.delete_question(question_id)

    def delete_survey(self, survey_id: int) -> types.OperationStatus:
        """Delete a survey.

        Calls :rpc_method:`delete_survey`.

        Args:
            survey_id: Survey to delete.

        Returns:
            Status message.

        .. versionadded:: 0.0.1
        """
        return self.session.delete_survey(survey_id)

    def export_responses(
        self,
        survey_id: int,
        *,
        token: str | None = None,
        file_format: str | enums.ResponsesExportFormat = "json",
        language: str | None = None,
        completion_status: str | enums.SurveyCompletionStatus = "all",
        heading_type: str | enums.HeadingType = "code",
        response_type: str | enums.ResponseType = "short",
        from_response_id: int | None = None,
        to_response_id: int | None = None,
        fields: t.Sequence[str] | None = None,
    ) -> bytes:
        """Export responses to a file-like object.

        Calls :rpc_method:`export_responses`.

        Args:
            survey_id: Survey to add the response to.
            token: Optional participant token to get responses for.
            file_format: Type of export. One of PDF, CSV, XLS, DOC or JSON.
            language: Export responses made to this language version of the survey.
            completion_status: Incomplete, complete or all.
            heading_type: Use response codes, long or abbreviated titles.
            response_type: Export long or short text responses.
            from_response_id: First response to export.
            to_response_id: Last response to export.
            fields: Which response fields to export. If none, exports all fields.

        Returns:
            Content bytes of exported to file.

        .. versionadded:: 0.0.1

        .. versionchanged:: 0.0.2
           Return raw bytes instead of number of bytes written.
        """
        if token is None:
            return base64.b64decode(
                self.session.export_responses(
                    survey_id,
                    enums.ResponsesExportFormat(file_format),
                    language,
                    enums.SurveyCompletionStatus(completion_status),
                    enums.HeadingType(heading_type),
                    enums.ResponseType(response_type),
                    from_response_id,
                    to_response_id,
                    fields,
                ),
            )

        return base64.b64decode(
            self.session.export_responses_by_token(
                survey_id,
                enums.ResponsesExportFormat(file_format),
                token,
                language,
                enums.SurveyCompletionStatus(completion_status),
                enums.HeadingType(heading_type),
                enums.ResponseType(response_type),
                from_response_id,
                to_response_id,
                fields,
            ),
        )

    def save_responses(  # noqa: PLR0913
        self,
        filename: PathLike[str],
        survey_id: int,
        *,
        token: str | None = None,
        file_format: str = "json",
        language: str | None = None,
        completion_status: str = "all",
        heading_type: str = "code",
        response_type: str = "short",
        from_response_id: int | None = None,
        to_response_id: int | None = None,
        fields: t.Sequence[str] | None = None,
    ) -> int:
        """Save responses to a file.

        Args:
            filename: Target file path.
            survey_id: Survey to add the response to.
            token: Optional participant token to get responses for.
            file_format: Type of export. One of PDF, CSV, XLS, DOC or JSON.
            language: Export responses made to this language version of the survey.
            completion_status: Incomplete, complete or all.
            heading_type: Use response codes, long or abbreviated titles.
            response_type: Export long or short text responses.
            from_response_id: First response to export.
            to_response_id: Last response to export.
            fields: Which response fields to export. If none, exports all fields.

        Returns:
            Bytes length written to file.

        .. versionadded:: 0.0.10
        """
        with Path(filename).open("wb") as f:
            return f.write(
                self.export_responses(
                    survey_id,
                    token=token,
                    file_format=file_format,
                    language=language,
                    completion_status=completion_status,
                    heading_type=heading_type,
                    response_type=response_type,
                    from_response_id=from_response_id,
                    to_response_id=to_response_id,
                    fields=fields,
                ),
            )

    def export_statistics(
        self,
        survey_id: int,
        *,
        file_format: str | enums.StatisticsExportFormat = "pdf",
        language: str | None = None,
        graph: bool = False,
        group_ids: list[int] | None = None,
    ) -> bytes:
        """Export survey statistics.

        Calls :rpc_method:`export_statistics`.

        Args:
            survey_id: ID of the Survey.
            file_format: Type of documents the exported statistics should be.
                Defaults to "pdf".
            language: Language of the survey to use (default from Survey).
                Defaults to None.
            graph: Export graphs. Defaults to False.
            group_ids: Question groups to generate statistics from. Defaults to None.

        Returns:
            File contents.

        .. versionadded:: 0.0.10
        """
        return base64.b64decode(
            self.session.export_statistics(
                survey_id,
                enums.StatisticsExportFormat(file_format),
                language,
                "yes" if graph else "no",
                group_ids,
            ),
        )

    def save_statistics(
        self,
        filename: PathLike[str],
        survey_id: int,
        *,
        file_format: str = "pdf",
        language: str | None = None,
        graph: bool = False,
        group_ids: list[int] | None = None,
    ) -> int:
        """Save survey statistics to a file.

        Args:
            filename: Target file path.
            survey_id: ID of the Survey.
            file_format: Type of documents the exported statistics should be.
                Defaults to "pdf".
            language: Language of the survey to use (default from Survey).
                Defaults to None.
            graph: Export graphs. Defaults to False.
            group_ids: Question groups to generate statistics from. Defaults to None.

        Returns:
            Bytes length written to file.
        """
        with Path(filename).open("wb") as f:
            return f.write(
                self.export_statistics(
                    survey_id,
                    file_format=file_format,
                    language=language,
                    graph=graph,
                    group_ids=group_ids,
                ),
            )

    def export_timeline(
        self,
        survey_id: int,
        period: t.Literal["day", "hour"] | enums.TimelineAggregationPeriod,
        start: datetime.datetime,
        end: datetime.datetime | None = None,
    ) -> dict[str, int]:
        """Export survey submission timeline.

        Calls :rpc_method:`export_timeline`.

        Args:
            survey_id: ID of the Survey.
            period: Granularity level for aggregation submission counts.
            start: Start datetime.
            end: End datetime.

        Returns:
            Mapping of days/hours to submission counts.

        .. versionadded:: 0.0.10
        """
        return self.session.export_timeline(
            survey_id,
            enums.TimelineAggregationPeriod(period),
            start.isoformat(),
            end.isoformat()
            if end
            else datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        )

    def get_group_properties(
        self,
        group_id: int,
        *,
        settings: list[str] | None = None,
        language: str | None = None,
    ) -> types.GroupProperties:
        """Get the properties of a group of a survey.

        Calls :rpc_method:`get_group_properties`.

        Args:
            group_id: ID of the group to get properties of.
            settings: Properties to get, default to all.
            language: Parameter language for multilingual groups.

        Returns:
            Dictionary of group properties.

        .. versionadded:: 0.0.10
        """
        return self.session.get_group_properties(group_id, settings, language)

    def get_language_properties(
        self,
        survey_id: int,
        *,
        settings: list[str] | None = None,
        language: str | None = None,
    ) -> types.LanguageProperties:
        """Get survey language properties.

        Args:
            survey_id: ID of the survey.
            settings: Properties to get, default to all.
            language: Specify language for multilingual surveys.

        Returns:
            Dictionary of survey language properties.

        .. versionadded:: 0.0.10
        """
        return self.session.get_language_properties(survey_id, settings, language)

    def get_participant_properties(
        self,
        survey_id: int,
        query: dict[str, t.Any] | int,
        properties: t.Sequence[str] | None = None,
    ) -> dict[str, t.Any]:
        """Get properties a single survey participant.

        Calls :rpc_method:`get_participant_properties`.

        Args:
            survey_id: Survey to get participants properties.
            query: Mapping of properties to query participants, or the token id
                as an integer.
            properties: Which participant properties to retrieve.

        Returns:
            List of participants properties.

        .. versionadded:: 0.0.1
        """
        return self.session.get_participant_properties(survey_id, query, properties)

    def get_question_properties(
        self,
        question_id: int,
        *,
        settings: list[str] | None = None,
        language: str | None = None,
    ) -> types.QuestionProperties:
        """Get properties of a question in a survey.

        Calls :rpc_method:`get_question_properties`.

        Args:
            question_id: ID of the question to get properties.
            settings: Properties to get, default to all.
            language: Parameter language for multilingual questions.

        Returns:
            Dictionary of question properties.

        .. versionadded:: 0.0.10
        """
        return self.session.get_question_properties(question_id, settings, language)

    def get_quota_properties(
        self,
        quota_id: int,
        settings: list[str] | None = None,
        language: str | None = None,
    ) -> types.QuotaProperties:
        """Get properties of a LimeSurvey quota.

        Calls :rpc_method:`get_quota_properties`.

        Args:
            quota_id: ID of the quota to get properties for.
            settings: Properties to get, default to all.
            language: Parameter language for multilingual quotas.

        Returns:
            Quota properties.

        .. versionadded:: 0.6.0
        .. minlimesurvey:: 6.0.0
        """
        return self.session.get_quota_properties(quota_id, settings, language)

    def get_response_ids(
        self,
        survey_id: int,
        token: str,
    ) -> list[int]:
        """Find response IDs given a survey ID and a token.

        Calls :rpc_method:`get_response_ids`.

        Args:
            survey_id: Survey to get responses from.
            token: Participant for which to get response IDs.

        Returns:
            A list of response IDs.

        .. versionadded:: 0.0.1
        """
        return self.session.get_response_ids(survey_id, token)

    def get_available_site_settings(self) -> list[str]:
        """Get all available site settings.

        Calls :rpc_method:`get_available_site_settings`.

        Returns:
            A list of all the available site settings.

        .. versionadded:: 0.6.0
        .. minlimesurvey:: 6.0.0
        """
        return self.session.get_available_site_settings()

    def _get_site_setting(self, setting_name: str) -> types.Result:
        """Get a global setting.

        Function to query site settings. Can only be used by super administrators.

        Args:
            setting_name: Name of the setting to get.

        Returns:
            The requested setting value.

        .. versionadded:: 0.0.1
        """
        return self.session.get_site_settings(setting_name)

    def get_default_theme(self) -> str:
        """Get the global default theme.

        Calls :rpc_method:`get_site_settings("defaulttheme") <get_site_settings>`.

        Returns:
            The name of the theme.

        .. versionadded:: 0.0.1
        """
        return self._get_site_setting("defaulttheme")

    def get_site_name(self) -> str:
        """Get the site name.

        Calls :rpc_method:`get_site_settings("sitename") <get_site_settings>`.

        Returns:
            The name of the site.

        .. versionadded:: 0.0.1
        """
        return self._get_site_setting("sitename")

    def get_default_language(self) -> str:
        """Get the default site language.

        Calls :rpc_method:`get_site_settings("defaultlang") <get_site_settings>`.

        Returns:
            A string representing the language.

        .. versionadded:: 0.0.1
        """
        return self._get_site_setting("defaultlang")

    def get_available_languages(self) -> list[str] | None:
        """Get the list of available languages.

        Calls
        :rpc_method:`get_site_settings("restrictToLanguages") <get_site_settings>`.

        Returns:
            Either a list of strings for the available languages or None if there are
            no restrictions.

        .. versionadded:: 0.0.1
        """
        langs: str = self._get_site_setting("restrictToLanguages")

        return langs.split(" ") if langs else None

    def get_server_version(self) -> str:
        """Get the server version.

        Calls :rpc_method:`get_site_settings("versionnumber") <get_site_settings>`.

        Returns:
            The LimeSurvey server version.

        .. versionadded:: 0.9.0
        """
        return self._get_site_setting("versionnumber")

    def get_db_version(self) -> int:
        """Get the LimeSurvey database version.

        Calls :rpc_method:`get_site_settings("dbversionnumber") <get_site_settings>`.

        Returns:
            The LimeSurvey database version.

        .. versionadded:: 1.0.0
        """
        return self._get_site_setting("dbversionnumber")

    def get_summary(self, survey_id: int) -> dict[str, int]:
        """Get survey summary.

        Calls :rpc_method:`get_summary`.

        Args:
            survey_id: ID of the survey to get summary of.

        Returns:
            Mapping of survey statistics.

        .. versionadded:: 0.0.10
        """
        return self.session.get_summary(survey_id)

    def get_survey_properties(
        self,
        survey_id: int,
        properties: t.Sequence[str] | None = None,
    ) -> types.SurveyProperties:
        """Get properties of a survey.

        Calls :rpc_method:`get_survey_properties`.

        Args:
            survey_id: Survey to get properties.
            properties: Which survey properties to retrieve. If none, gets all fields.

        Returns:
            Dictionary of survey properties.

        .. versionadded:: 0.0.1
        """
        return self.session.get_survey_properties(survey_id, properties)

    def get_uploaded_files(
        self,
        survey_id: int,
        token: str | None = None,
    ) -> dict[str, dict[str, t.Any]]:
        """Get a dictionary of files uploaded in a survey response.

        Calls :rpc_method:`get_uploaded_files`.

        Args:
            survey_id: Survey for which to download files.
            token: Optional participant token to filter uploaded files.

        Returns:
            Dictionary with uploaded files metadata.

        .. versionadded:: 0.0.5
        """
        return self.session.get_uploaded_files(survey_id, token)

    def get_uploaded_file_objects(
        self,
        survey_id: int,
        token: str | None = None,
    ) -> t.Generator[UploadedFile, None, None]:
        """Iterate over uploaded files in a survey response.

        Args:
            survey_id: Survey for which to download files.
            token: Optional participant token to filter uploaded files.

        Yields:
            :class:`~citric.client.UploadedFile` objects.

        .. versionadded:: 0.0.13
        """
        files_data = self.get_uploaded_files(survey_id, token)
        for file in files_data:
            metadata: dict[str, t.Any] = files_data[file]["meta"]
            question: dict[str, t.Any] = metadata.pop("question")
            content = base64.b64decode(files_data[file]["content"])

            yield UploadedFile(
                meta=FileMetadata(
                    **metadata,
                    question=QuestionReference(**question),
                ),
                content=io.BytesIO(content),
            )

    def download_files(
        self,
        directory: str | Path,
        survey_id: int,
        token: str | None = None,
    ) -> list[Path]:
        """Download files uploaded in survey response.

        Args:
            directory: Where to store the files.
            survey_id: Survey for which to download files.
            token: Optional participant token to filter uploaded files.

        Returns:
            List with the paths of downloaded files.

        .. versionadded:: 0.0.1
        """
        dirpath = Path(directory)

        filepaths = []
        uploaded_files = self.get_uploaded_file_objects(survey_id, token=token)

        for file in uploaded_files:
            filepath = dirpath / file.meta.filename
            filepaths.append(filepath)
            with Path(filepath).open("wb") as f:
                f.write(file.content.read())

        return filepaths

    def import_group(
        self,
        file: t.IO[bytes],
        survey_id: int,
        file_type: str | enums.ImportGroupType = "lsg",
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> int:
        """Import group from a file.

        Create a new group from an exported LSG file.

        Calls :rpc_method:`import_group`.

        Args:
            file: File object.
            survey_id: The ID of the Survey that the question will belong to.
            file_type: Type of file. One of LSS, CSV, TXT and LSA.
            name: Optional new name for the group.
            description: Optional new description for the group.

        Returns:
            The ID of the new group.

        .. code-block:: python

            with open("group.lsg", "rb") as f:
                group_id = client.import_group(f, survey_id)

        .. versionadded:: 0.0.10
        .. versionchanged:: NEXT_VERSION
           Added the ``name`` and ``description`` optional parameters.
        """
        contents = base64.b64encode(file.read()).decode()
        return self.session.import_group(
            survey_id,
            contents,
            enums.ImportGroupType(file_type),
            name,
            description,
        )

    def import_question(
        self,
        file: t.IO[bytes],
        survey_id: int,
        group_id: int,
    ) -> int:
        """Import question from a file.

        Create a new question from an exported LSQ file.

        TODO: Check support for additional fields like custom title, text, etc.

        Calls :rpc_method:`import_question`.

        Args:
            file: File object.
            survey_id: The ID of the Survey that the question will belong to.
            group_id: The ID of the Group that the question will belong to.

        Returns:
            The ID of the new question.

        .. versionadded:: 0.0.8
        """
        contents = base64.b64encode(file.read()).decode()
        return self.session.import_question(
            survey_id,
            group_id,
            contents,
            "lsq",
        )

    def import_survey(
        self,
        file: t.IO[bytes],
        file_type: str | enums.ImportSurveyType = "lss",
        survey_name: str | None = None,
        survey_id: int | None = None,
    ) -> int:
        """Import survey from a file.

        Create a new survey from an exported LSS, CSV, TXT or LSA file.

        Calls :rpc_method:`import_survey`.

        .. warning::
           Different versions of LimeSurvey seem to expect slightly different structures
           for exported files. If you get errors when importing a survey, try importing
           it manually in the LimeSurvey web interface. If it works, try exporting it
           from the web interface and importing the new file. If it still doesn't work,
           you might need to import it with a different version of LimeSurvey.

        Args:
            file: File object.
            file_type: Type of file. One of LSS, CSV, TXT and LSA.
            survey_name: Override the new survey name.
            survey_id: Desired ID of the new survey. A different ID will be used if
                there is already a survey with this ID.

        Returns:
            The ID of the new survey.

        .. versionadded:: 0.0.1
        .. versionchanged:: 0.0.5
           Accept a binary file object instead of a path.
        """
        contents = base64.b64encode(file.read()).decode()
        return self.session.import_survey(
            contents,
            enums.ImportSurveyType(file_type),
            survey_name,
            survey_id,
        )

    def list_participants(
        self,
        survey_id: int,
        *,
        start: int = 0,
        limit: int = 10,
        unused: bool = False,
        attributes: t.Sequence[str] | bool = False,
        conditions: t.Mapping[str, t.Any] | None = None,
    ) -> list[dict[str, t.Any]]:
        """Get participants in a survey.

        Calls :rpc_method:`list_participants`.

        Args:
            survey_id: Survey to get participants from.
            start: Retrieve participants starting from this index (zero-indexed).
            limit: Maximum number of participants to retrieve.
            unused: Retrieve participants with unused tokens.
            attributes: Extra participant attributes to include in the result.
            conditions: Dictionary of conditions to limit the list.

        Returns:
            List of participants with basic information.

        Some valid participant attributes are:

        * tid
        * participant_id
        * firstname
        * lastname
        * email
        * emailstatus
        * token
        * language
        * blacklisted
        * sent
        * remindersent
        * remindercount
        * completed
        * usesleft
        * validfrom
        * validuntil

        .. versionadded:: 0.0.1
        .. versionchanged:: 0.4.0
           Use keyword-only arguments.
        """
        return self.session.list_participants(
            survey_id,
            start,
            limit,
            unused,
            attributes,
            conditions or {},
        )

    def list_users(self) -> list[dict[str, t.Any]]:
        """Get LimeSurvey users.

        Calls :rpc_method:`list_users`.

        Returns:
            List of users.

        .. versionadded:: 0.0.3
        """
        return self.session.list_users()

    def list_groups(
        self,
        survey_id: int,
        language: str | None = None,
    ) -> list[dict[str, t.Any]]:
        """Get the IDs and all attributes of all question groups in a Survey.

        Calls :rpc_method:`list_groups`.

        Args:
            survey_id: ID of the Survey containing the groups.
            language: Optional parameter language for multilingual groups.

        Returns:
            List of question groups.

        .. versionadded:: 0.0.10
        """
        return self.session.list_groups(survey_id, language)

    def list_questions(
        self,
        survey_id: int,
        group_id: int | None = None,
        language: str | None = None,
    ) -> list[types.QuestionsListElement]:
        """Get questions in a survey, in a specific group or all.

        Calls :rpc_method:`list_questions`.

        Args:
            survey_id: Survey.
            group_id: Question group.
            language: Retrieve question text, description, etc. in this language.

        Returns:
            List of questions with basic information.

        .. versionadded:: 0.0.1
        """
        return self.session.list_questions(survey_id, group_id, language)

    def list_quotas(self, survey_id: int) -> list[types.QuotaListElement]:
        """Get all quotas for a LimeSurvey survey.

        Calls :rpc_method:`list_quotas`.

        Args:
            survey_id: ID of the survey to get quotas for.

        Returns:
            List of quotas.

        .. versionadded:: 0.6.0
        .. minlimesurvey:: 6.0.0
        """
        return self.session.list_quotas(survey_id)

    def list_surveys(self, username: str | None = None) -> list[dict[str, t.Any]]:
        """Get all surveys or only those owned by a user.

        Calls :rpc_method:`list_surveys`.

        Args:
            username: Owner of the surveys to retrieve.

        Returns:
            List of surveys with basic information.

        .. versionadded:: 0.0.1
        """
        return self.session.list_surveys(username)

    def list_survey_groups(
        self,
        username: str | None = None,
    ) -> list[dict[str, t.Any]]:
        """Get all survey groups or only those owned by a user.

        Calls :rpc_method:`list_survey_groups`.

        Args:
            username: Owner of the survey groups to retrieve.

        Returns:
            List of survey groups with basic information.

        .. versionadded:: 0.0.2
        """
        return self.session.list_survey_groups(username)

    def set_group_properties(
        self,
        group_id: int,
        **properties: Unpack[types.GroupProperties],
    ) -> dict[str, bool]:
        """Set properties of a group.

        Calls :rpc_method:`set_group_properties`.

        Args:
            group_id: ID of the group.
            properties: Properties to set.

        Returns:
            Mapping of property names to whether they were set successfully.

        .. versionadded:: 0.0.11
        """
        return self.session.set_group_properties(group_id, properties)

    def set_language_properties(
        self,
        survey_id: int,
        language: str | None = None,
        **properties: Unpack[types.LanguageProperties],
    ) -> dict[str, t.Any]:
        """Set properties of a survey language.

        Calls :rpc_method:`set_language_properties`.

        Args:
            survey_id: ID of the survey for which to set the language properties.
            language: Language code.
            properties: Properties to set.

        Returns:
            Mapping with status and updated properties.

        .. versionadded:: 0.0.11
        """
        return self.session.set_language_properties(survey_id, properties, language)

    def set_participant_properties(
        self,
        survey_id: int,
        token_query_properties: t.Mapping[str, t.Any] | int,
        **token_data: t.Any,
    ) -> dict[str, t.Any]:
        """Set properties of a participant. Only one participant can be updated.

        Calls :rpc_method:`set_participant_properties`.

        Args:
            survey_id: ID of the survey to which the participant belongs.
            token_query_properties: Dictionary of properties to match the participant
                or token ID.
            token_data: Properties to set.

        Returns:
            New participant properties.

        .. versionadded:: 0.0.11
        """
        return self.session.set_participant_properties(
            survey_id,
            token_query_properties,
            token_data,
        )

    def set_question_properties(
        self,
        question_id: int,
        language: str | None = None,
        **properties: Unpack[types.QuestionProperties],
    ) -> dict[str, bool]:
        """Set properties of a question.

        Args:
            question_id: ID of the question to set the properties of.
            language: Language code.
            properties: Properties to set.

        Returns:
            Mapping of property names to whether they were set successfully.

        .. versionadded:: 0.0.11
        """
        return self.session.set_question_properties(question_id, properties, language)

    def set_quota_properties(
        self,
        quota_id: int,
        **properties: Unpack[types.QuotaProperties],
    ) -> types.SetQuotaPropertiesResult:
        """Set properties of a quota.

        Calls :rpc_method:`set_quota_properties`.

        Args:
            quota_id: Quota ID.
            properties: Properties to set.

        Returns:
            Mapping with success status and updated properties.

        .. versionadded:: 0.6.0
        """
        return self.session.set_quota_properties(quota_id, properties)

    def set_survey_properties(
        self,
        survey_id: int,
        **properties: Unpack[types.SurveyProperties],
    ) -> dict[str, bool]:
        """Set properties of a survey.

        Calls :rpc_method:`set_survey_properties`.

        Args:
            survey_id: ID of the survey to set the properties of.
            properties: Properties to set.

        Returns:
            Mapping of property names to whether they were set successfully.

        .. versionadded:: 0.0.11
        """
        return self.session.set_survey_properties(survey_id, properties)

    def upload_file_object(
        self,
        survey_id: int,
        field: str,
        filename: str,
        file: t.IO[bytes],
    ) -> types.FileUploadResult:
        """Upload a file to a LimeSurvey survey.

        Calls :rpc_method:`upload_file`.

        Args:
            survey_id: ID of the survey to upload the file to.
            field: Field name to upload the file to.
            filename: Name of the file to upload.
            file: File-like object to upload.

        Returns:
            File metadata with final upload path.

        .. versionadded:: 0.0.14
        """
        contents = base64.b64encode(file.read()).decode()
        return self.session.upload_file(survey_id, field, filename, contents)

    def upload_file(
        self,
        survey_id: int,
        field: str,
        path: PathLike[str],
        *,
        filename: str | None = None,
    ) -> types.FileUploadResult:
        """Upload a file to a LimeSurvey survey from a local path.

        Args:
            survey_id: ID of the survey to which the file belongs.
            field: Field to upload the file to.
            path: Path to the file to upload.
            filename: Optional filename override to use in LimeSurvey.

        Returns:
            File metadata with final upload path.

        .. versionadded:: 0.0.14
        """
        path = Path(path)
        if filename is None:
            filename = path.name

        with Path(path).open("rb") as file:
            return self.upload_file_object(survey_id, field, filename, file)

    def invite_participants(
        self,
        survey_id: int,
        *,
        token_ids: list[int] | None = None,
        strategy: int = enums.EmailSendStrategy.PENDING,
    ) -> int:
        """Invite participants to a survey.

        Calls :rpc_method:`invite_participants`.

        Args:
            survey_id: ID of the survey to invite participants to.
            token_ids: IDs of the participants to invite.
            strategy: Strategy to use for sending emails. See
                :class:`~citric.enums.EmailSendStrategy`.

        Returns:
            Number of emails left to send.

        Raises:
            LimeSurveyStatusError: If the number of emails left to send could not be
                determined.
            RuntimeError: If an unexpected error occurs.

        .. versionadded:: 0.8.0
        """
        email_flag = enums.EmailSendStrategy.to_flag(strategy)
        try:
            self.session.invite_participants(survey_id, token_ids, email_flag)
        except LimeSurveyStatusError as error:
            status_match = re.match(EMAILS_SENT_STATUS_PATTERN, error.args[0])
            if not status_match:
                raise

            return int(status_match[1])

        msg = "Could not determine invitation status"
        raise RuntimeError(msg)
