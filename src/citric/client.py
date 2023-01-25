"""Python API Client."""

from __future__ import annotations

import base64
import datetime
import io
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import requests

from citric import enums
from citric.session import Session

if TYPE_CHECKING:
    import sys
    from os import PathLike
    from types import TracebackType
    from typing import Any, BinaryIO, Generator, Iterable, Mapping, Sequence

    if sys.version_info >= (3, 8):
        from typing import Literal
    else:
        from typing_extensions import Literal


_T = TypeVar("_T", bound="Client")


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
    """File content as `io.BytesIO`_.

    .. _io.BytesIO:
        https://docs.python.org/3/library/io.html#io.BytesIO
    """


class Client:
    """LimeSurvey Remote Control client.

    Offers explicit wrappers for RPC methods and simplifies common workflows.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A `requests.Session`_ object.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).

    .. _requests.Session:
        https://requests.readthedocs.io/en/latest/api/#request-sessions
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
        """Create a LimeSurvey Python API client."""
        self.__session = self.session_class(
            url,
            username,
            password,
            requests_session=requests_session or requests.session(),
            auth_plugin=auth_plugin,
        )

    def close(self) -> None:
        """Close client session."""
        self.__session.close()

    def __enter__(self: _T) -> _T:
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

    def get_fieldmap(self, survey_id: int) -> dict:
        """Get fieldmap for a survey.

        Args:
            survey_id: ID of survey to get fieldmap for.

        Returns:
            Dictionary mapping response keys to LimeSurvey internal representation.
        """
        return self.__session.get_fieldmap(survey_id)

    def activate_survey(self, survey_id: int) -> dict[str, Any]:
        """Activate a survey.

        Args:
            survey_id: ID of survey to be activated.

        Returns:
            Status and plugin feedback.
        """
        return self.__session.activate_survey(survey_id)

    def activate_tokens(
        self,
        survey_id: int,
        attributes: list[int] | None = None,
    ) -> dict[str, str]:
        """Initialise the survey participant table.

        New participant tokens may be later added.

        Args:
            survey_id: ID of survey to be activated.
            attributes: Optional list of participant attributes numbers to be activated.

        Returns:
            Status message.
        """
        return self.__session.activate_tokens(survey_id, attributes or [])

    def add_language(self, survey_id: int, language: str) -> dict[str, Any]:
        """Add a survey language.

        Args:
            survey_id: ID of the Survey for which a language will be added.
            language: A valid language shortcut to add to the current Survey. If the
                language already exists no error will be given.

        Returns:
            Status message.
        """
        return self.__session.add_language(survey_id, language)

    def add_participants(
        self,
        survey_id: int,
        *,
        participant_data: Sequence[Mapping[str, Any]],
        create_tokens: bool = True,
    ) -> list[dict[str, Any]]:
        """Add participants to a survey.

        Args:
            survey_id: Survey to add participants to.
            participant_data: Information to create participants with.
            create_tokens: Whether to create the participants with tokens.

        Returns:
            Information of newly created participants.
        """
        return self.__session.add_participants(
            survey_id,
            participant_data,
            create_tokens,
        )

    def add_survey(
        self,
        survey_id: int,
        title: str,
        language: str,
        survey_format: str = "G",
    ) -> int:
        """Add a new empty survey.

        Args:
            survey_id: The desired ID of the Survey to add.
            title: Title of the new Survey.
            language: Default language of the Survey.
            survey_format: Question appearance format (A, G or S) for "All on one page",
                "Group by Group", "Single questions", default to group by group (G).

        Returns:
            The new survey ID.
        """
        return self.__session.add_survey(
            survey_id,
            title,
            language,
            enums.NewSurveyType(survey_format),
        )

    def delete_participants(
        self,
        survey_id: int,
        participant_ids: Sequence[int],
    ) -> list[dict[str, Any]]:
        """Add participants to a survey.

        Args:
            survey_id: Survey to delete participants to.
            participant_ids: Participant IDs to be deleted.

        Returns:
            Information of removed participants.
        """
        return self.__session.delete_participants(
            survey_id,
            participant_ids,
        )

    def _get_question_mapping(
        self,
        survey_id: int,
    ) -> dict[str, dict[str, Any]]:
        """Get question mapping.

        Args:
            survey_id: Survey ID.

        Returns:
            Question mapping.
        """
        return {q["title"]: q for q in self.list_questions(survey_id)}

    @staticmethod
    def _map_response_keys(
        response_data: Mapping[str, Any],
        question_mapping: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Convert response keys to LimeSurvey's internal representation.

        Args:
            response_data: The response mapping.
            question_mapping: A mapping of question titles to question dictionaries.

        Returns:
            A new dictionary with the keys mapped to the <SID>X<GID>X<QID> format.

        >>> mapped_keys = Client._map_response_keys(
        ...     {"Q1": "foo", "Q2": "bar", "BAZ": "qux"},
        ...     {
        ...         "Q1": {
        ...             "title": "Q1",
        ...             "qid": 9,
        ...             "gid": 7,
        ...             "sid": 123,
        ...         },
        ...         "Q2": {
        ...             "title": "Q2",
        ...             "qid": 10,
        ...             "gid": 7,
        ...             "sid": 123,
        ...         },
        ...     },
        ... )
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

        Args:
            survey_id: ID of the Survey to add the group.
            title: Name of the group.
            description: Optional description of the group.

        Returns:
            The id of the new group.
        """
        return self.__session.add_group(survey_id, title, description)

    def _add_response(self, survey_id: int, response_data: Mapping[str, Any]) -> int:
        """Add a single response to a survey.

        Args:
            survey_id: Survey to add the response to.
            response_data: Single response as a mapping from question codes of the form
                <SID>X<GID>X<QID> to response values.

        Returns:
            ID of the new response.
        """
        return int(self.__session.add_response(survey_id, response_data))

    def add_response(self, survey_id: int, response_data: Mapping[str, Any]) -> int:
        """Add a single response to a survey.

        Args:
            survey_id: Survey to add the response to.
            response_data: Single response as a mapping.

        Returns:
            ID of the new response.
        """
        # Transform question codes to the format LimeSurvey expects
        questions = self._get_question_mapping(survey_id)
        data = self._map_response_keys(response_data, questions)
        return self._add_response(survey_id, data)

    def add_responses(
        self,
        survey_id: int,
        responses: Iterable[Mapping[str, Any]],
    ) -> list[int]:
        """Add multiple responses to a survey.

        Args:
            survey_id: Survey to add the response to.
            responses: Iterable of survey responses.

        Returns:
            IDs of the new responses.
        """
        ids = []
        questions = self._get_question_mapping(survey_id)
        for response in responses:
            data = self._map_response_keys(response, questions)
            response_id = self._add_response(survey_id, data)
            ids.append(response_id)
        return ids

    def update_response(self, survey_id: int, response_data: dict[str, Any]) -> bool:
        """Update a response.

        Args:
            survey_id: Survey to update the response in.
            response_data: Response data to update.

        Returns:
            True if the response was updated, False otherwise.
        """
        questions = self._get_question_mapping(survey_id)
        data = self._map_response_keys(response_data, questions)
        return self.__session.update_response(survey_id, data)

    def copy_survey(self, survey_id: int, name: str) -> dict[str, Any]:
        """Copy a survey.

        Args:
            survey_id: ID of the source survey.
            name: Name of the new survey.

        Returns:
            Dictionary of status message and the new survey ID.
        """
        return self.__session.copy_survey(survey_id, name)

    def delete_group(self, survey_id: int, group_id: int) -> int:
        """Delete a group.

        Args:
            survey_id: ID of the Survey that the group belongs to.
            group_id: ID of the group to delete.

        Returns:
            ID of the deleted group.
        """
        return self.__session.delete_group(survey_id, group_id)

    def delete_language(self, survey_id: int, language: str) -> dict[str, str]:
        """Delete a language from a survey.

        Requires at LimeSurvey >= 5.3.4.

        Args:
            survey_id: ID of the Survey for which a language will be deleted from.
            language: Language to delete.

        Returns:
            Status message.
        """
        return self.__session.delete_language(survey_id, language)

    def delete_response(self, survey_id: int, response_id: int) -> dict[str, str]:
        """Delete a response in a survey.

        Args:
            survey_id: ID of the survey the response belongs to.
            response_id: ID of the response to delete.

        Returns:
            Status message.
        """
        return self.__session.delete_response(survey_id, response_id)

    def delete_question(self, question_id: int) -> int:
        """Delete a survey.

        Requires at least LimeSurvey 5.3.19+220607.

        TODO: Add links to issue, PR, etc.

        Args:
            question_id: ID of Question to delete.

        Returns:
            ID of the deleted question.
        """
        return self.__session.delete_question(question_id)

    def delete_survey(self, survey_id: int) -> dict[str, str]:
        """Delete a survey.

        Args:
            survey_id: Survey to delete.

        Returns:
            Status message.
        """
        return self.__session.delete_survey(survey_id)

    def export_responses(
        self,
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
        fields: Sequence[str] | None = None,
    ) -> bytes:
        """Export responses to a file-like object.

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
        """
        if token is None:
            return base64.b64decode(
                self.__session.export_responses(
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
            self.__session.export_responses_by_token(
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

    def save_responses(
        self,
        filename: PathLike,
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
        fields: Sequence[str] | None = None,
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
        file_format: str = "pdf",
        language: str | None = None,
        graph: bool = False,
        group_ids: list[int] | None = None,
    ) -> bytes:
        """Export survey statistics.

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
        filename: PathLike,
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
        period: Literal["day", "hour"],
        start: datetime.datetime,
        end: datetime.datetime | None = None,
    ) -> dict[str, int]:
        """Export survey submission timeline.

        Args:
            survey_id: ID of the Survey.
            period: Granularity level for aggregation submission counts.
            start: Start datetime.
            end: End datetime.

        Returns:
            Mapping of days/hours to submission counts.
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
    ) -> dict[str, Any]:
        """Get the properties of a group of a survey.

        Args:
            group_id: ID of the group to get properties of.
            settings: Properties to get, default to all.
            language: Parameter language for multilingual groups.

        Returns:
            Dictionary of group properties.
        """
        return self.__session.get_group_properties(group_id, settings, language)

    def get_language_properties(
        self,
        survey_id: int,
        *,
        settings: list[str] | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Get survey language properties.

        Args:
            survey_id: ID of the survey.
            settings: Properties to get, default to all.
            language: Parameter language for multilingual questions.

        Returns:
            Dictionary of survey language properties.
        """
        return self.__session.get_language_properties(survey_id, settings, language)

    def get_participant_properties(
        self,
        survey_id: int,
        query: dict[str, Any] | int,
        properties: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Get properties a single survey participant.

        Args:
            survey_id: Survey to get participants properties.
            query: Mapping of properties to query participants, or the token id
                as an integer.
            properties: Which participant properties to retrieve.

        Returns:
            List of participants properties.
        """
        return self.__session.get_participant_properties(survey_id, query, properties)

    def get_question_properties(
        self,
        question_id: int,
        *,
        settings: list[str] | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Get properties of a question in a survey.

        Args:
            question_id: ID of the question to get properties.
            settings: Properties to get, default to all.
            language: Parameter language for multilingual questions.

        Returns:
            Dictionary of question properties.
        """
        return self.__session.get_question_properties(question_id, settings, language)

    def get_response_ids(
        self,
        survey_id: int,
        token: str,
    ) -> list[int]:
        """Find response IDs given a survey ID and a token.

        Args:
            survey_id: Survey to get responses from.
            token: Participant for which to get response IDs.

        Returns:
            A list of response IDs.
        """
        return self.__session.get_response_ids(survey_id, token)

    def _get_site_setting(self, setting_name: str) -> Any:  # noqa: ANN401
        """Get a global setting.

        Function to query site settings. Can only be used by super administrators.

        Args:
            setting_name: Name of the setting to get.

        Returns:
            The requested setting value.
        """
        return self.__session.get_site_settings(setting_name)

    def get_default_theme(self) -> str:
        """Get the global default theme.

        Calls :rpc_method:`get_site_settings("defaulttheme") <get_site_settings>`.

        Returns:
            The name of the theme.
        """
        return self._get_site_setting("defaulttheme")

    def get_site_name(self) -> str:
        """Get the site name.

        Calls :rpc_method:`get_site_settings("sitename") <get_site_settings>`.

        Returns:
            The name of the site.
        """
        return self._get_site_setting("sitename")

    def get_default_language(self) -> str:
        """Get the default site language.

        Calls :rpc_method:`get_site_settings("defaultlang") <get_site_settings>`.

        Returns:
            A string representing the language.
        """
        return self._get_site_setting("defaultlang")

    def get_available_languages(self) -> list[str] | None:
        """Get the list of available languages.

        Calls
        :rpc_method:`get_site_settings("restrictToLanguages") <get_site_settings>`.

        Returns:
            Either a list of strings for the available languages or None if there are
            no restrictions.
        """
        langs: str = self._get_site_setting("restrictToLanguages")

        return langs.split(" ") if langs else None

    def get_summary(self, survey_id: int) -> dict[str, int]:
        """Get survey summary.

        Args:
            survey_id: ID of the survey to get summary of.

        Returns:
            Mapping of survey statistics.
        """
        return self.session.get_summary(survey_id)

    def get_survey_properties(
        self,
        survey_id: int,
        properties: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Get properties of a survey.

        Args:
            survey_id: Survey to get properties.
            properties: Which survey properties to retrieve. If none, gets all fields.

        Returns:
            Dictionary of survey properties.
        """
        return self.__session.get_survey_properties(survey_id, properties)

    def get_uploaded_files(
        self,
        survey_id: int,
        token: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Get a dictionary of files uploaded in a survey response.

        Args:
            survey_id: Survey for which to download files.
            token: Optional participant token to filter uploaded files.

        Returns:
            Dictionary with uploaded files metadata.
        """
        return self.__session.get_uploaded_files(survey_id, token)

    def get_uploaded_file_objects(
        self,
        survey_id: int,
        token: str | None = None,
    ) -> Generator[UploadedFile, None, None]:
        """Iterate over uploaded files in a survey response.

        Args:
            survey_id: Survey for which to download files.
            token: Optional participant token to filter uploaded files.

        Yields:
            :class:`~citric.client.UploadedFile` objects.
        """
        files_data = self.get_uploaded_files(survey_id, token)
        for file in files_data:
            metadata: dict = files_data[file]["meta"]
            question: dict = metadata.pop("question")
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
        file: BinaryIO,
        survey_id: int,
        file_type: str = "lsg",
    ) -> int:
        """Import group from a file.

        Create a new group from an exported LSG file.

        TODO: Check support for custom name and description.

        Args:
            file: File object.
            survey_id: The ID of the Survey that the question will belong to.
            file_type: Type of file. One of LSS, CSV, TXT and LSA.

        Returns:
            The ID of the new group.
        """
        contents = base64.b64encode(file.read()).decode()
        return self.__session.import_group(
            survey_id,
            contents,
            enums.ImportGroupType(file_type),
        )

    def import_question(
        self,
        file: BinaryIO,
        survey_id: int,
        group_id: int,
    ) -> int:
        """Import question from a file.

        Create a new question from an exported LSQ file.

        TODO: Check support for additional fields like custom title, text, etc.

        Args:
            file: File object.
            survey_id: The ID of the Survey that the question will belong to.
            group_id: The ID of the Group that the question will belong to.

        Returns:
            The ID of the new question.
        """
        contents = base64.b64encode(file.read()).decode()
        return self.__session.import_question(
            survey_id,
            group_id,
            contents,
            "lsq",
        )

    def import_survey(
        self,
        file: BinaryIO,
        file_type: str = "lss",
        survey_name: str | None = None,
        survey_id: int | None = None,
    ) -> int:
        """Import survey from a file.

        Create a new survey from an exported LSS, CSV, TXT or LSA file.

        Args:
            file: File object.
            file_type: Type of file. One of LSS, CSV, TXT and LSA.
            survey_name: Override the new survey name.
            survey_id: Desired ID of the new survey. A different ID will be used if
                there is already a survey with this ID.

        Returns:
            The ID of the new survey.
        """
        contents = base64.b64encode(file.read()).decode()
        return self.__session.import_survey(
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
        attributes: Sequence[str] | bool = False,
        conditions: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get participants in a survey.

        Args:
            survey_id: Survey to get participants from.
            start: Retrieve participants starting from this index (zero-indexed).
            limit: Maximum number of participants to retrieve.
            unused: Retrieve partipants with unused tokens.
            attributes: Extra participant attributes to include in the result.
            conditions: Dictionary of conditions to limit the list.

        Returns:
            List of participants with basic information.
        """
        return self.__session.list_participants(
            survey_id,
            start,
            limit,
            unused,
            attributes,
            conditions or {},
        )

    def list_users(self) -> list[dict[str, Any]]:
        """Get LimeSurvey users.

        Returns:
            List of users.
        """
        return self.__session.list_users()

    def list_groups(
        self,
        survey_id: int,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get the IDs and all attributes of all question groups in a Survey.

        Args:
            survey_id: ID of the Survey containing the groups.
            language: Optional parameter language for multilingual groups.

        Returns:
            List of question groups.
        """
        return self.__session.list_groups(survey_id, language)

    def list_questions(
        self,
        survey_id: int,
        group_id: int | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get questions in a survey, in a specific group or all.

        Args:
            survey_id: Survey.
            group_id: Question group.
            language: Retrieve question text, description, etc. in this language.

        Returns:
            List of questions with basic information.
        """
        return self.__session.list_questions(survey_id, group_id, language)

    def list_surveys(self, username: str | None = None) -> list[dict[str, Any]]:
        """Get all surveys or only those owned by a user.

        Args:
            username: Owner of the surveys to retrieve.

        Returns:
            List of surveys with basic information.
        """
        return self.__session.list_surveys(username)

    def list_survey_groups(
        self,
        username: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all survey groups or only those owned by a user.

        Args:
            username: Owner of the survey groups to retrieve.

        Returns:
            List of survey groups with basic information.
        """
        return self.__session.list_survey_groups(username)

    def set_group_properties(self, group_id: int, **properties: Any) -> dict[str, bool]:
        """Set properties of a group.

        Args:
            group_id: ID of the group.
            properties: Properties to set.

        Returns:
            Mapping of property names to whether they were set successfully.
        """
        return self.session.set_group_properties(group_id, properties)

    def set_language_properties(
        self,
        survey_id: int,
        language: str | None = None,
        **properties: Any,
    ) -> dict[str, Any]:
        """Set properties of a survey language.

        Args:
            survey_id: ID of the survey for which to set the language properties.
            language: Language code.
            properties: Properties to set.

        Returns:
            Mapping with status and updated properties.
        """
        return self.session.set_language_properties(survey_id, properties, language)

    def set_participant_properties(
        self,
        survey_id: int,
        token_query_properties: Mapping[str, Any] | int,
        **token_data: Any,
    ) -> dict[str, Any]:
        """Set properties of a participant. Only one particpant can be updated.

        Args:
            survey_id: ID of the survey to which the participant belongs.
            token_query_properties: Dictionary of properties to match the participant
                or token ID.
            token_data: Properties to set.

        Returns:
            New participant properties.
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
        **properties: Any,
    ) -> dict[str, bool]:
        """Set properties of a question.

        Args:
            question_id: ID of the question to set the properties of.
            language: Language code.
            properties: Properties to set.

        Returns:
            Mapping of property names to whether they were set successfully.
        """
        return self.session.set_question_properties(question_id, properties, language)

    def set_survey_properties(
        self,
        survey_id: int,
        **properties: Any,
    ) -> dict[str, bool]:
        """Set properties of a survey.

        Args:
            survey_id: ID of the survey to set the properties of.
            properties: Properties to set.

        Returns:
            Mapping of property names to whether they were set successfully.
        """
        return self.session.set_survey_properties(survey_id, properties)

    def upload_file_object(
        self,
        survey_id: int,
        field: str,
        filename: str,
        file: BinaryIO,
    ) -> dict[str, Any]:
        """Upload a file to a LimeSurvey survey.

        Args:
            survey_id: ID of the survey to upload the file to.
            field: Field name to upload the file to.
            filename: Name of the file to upload.
            file: File-like object to upload.

        Returns:
            File metadata with final upload path.
        """
        contents = base64.b64encode(file.read()).decode()
        return self.session.upload_file(survey_id, field, filename, contents)

    def upload_file(
        self,
        survey_id: int,
        field: str,
        path: PathLike,
        *,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """Upload a file to a LimeSurvey survey from a local path.

        Args:
            survey_id: ID of the survey to which the file belongs.
            field: Field to upload the file to.
            path: Path to the file to upload.
            filename: Optional filename override to use in LimeSurvey.

        Returns:
            File metadata with final upload path.
        """
        path = Path(path)
        if filename is None:
            filename = path.name

        with Path(path).open("rb") as file:
            return self.upload_file_object(survey_id, field, filename, file)
