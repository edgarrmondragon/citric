"""Python API Client."""

import base64
from pathlib import Path
from types import TracebackType
from typing import (
    Any,
    BinaryIO,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
)

import requests

from citric import enums
from citric.session import Session

_T = TypeVar("_T", bound="Client")


class Client:
    """LimeSurvey Remote Control client.

    Offers explicit wrappers for RPC methods and simplifies common workflows.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A `requests.Session`_ object.
        auth_plugin: Name of the `plugin` to use for authentication.
            For example, `AuthLDAP`_. Defaults to using the internal database
            (`Authdb`_).

    .. _requests.Session:
        https://docs.python-requests.org/en/latest/api/#requests.Session
    .. _plugin: https://manual.limesurvey.org/Authentication_plugins
    .. _Authdb: https://manual.limesurvey.org/Authentication_plugins#Internal_database
    .. _AuthLDAP: https://manual.limesurvey.org/Authentication_plugins#LDAP

    .. _requests.Session:
        https://docs.python-requests.org/en/latest/api/#requests.Session
    """

    session_class = Session

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: requests.Session = requests.session(),
        auth_plugin: str = "Authdb",
    ) -> None:
        """Create a LimeSurvey Python API client."""
        self.__session = self.session_class(
            url,
            username,
            password,
            requests_session=requests_session,
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
        type: Optional[Type[BaseException]],
        value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Safely exit the client context."""
        self.close()

    @property
    def session(self) -> Session:
        """Low-level RPC session."""
        return self.__session

    def activate_survey(self, survey_id: int) -> Dict[str, Any]:
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
        attributes: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Initialise the survey participant table.

        New participant tokens may be later added.

        Args:
            survey_id: ID of survey to be activated.
            attributes: Additional fields.

        Returns:
            Status message.
        """
        return self.__session.activate_tokens(survey_id)

    def add_participants(
        self,
        survey_id: int,
        participant_data: Sequence[Mapping[str, Any]],
        create_tokens: bool = True,
    ) -> List[Dict[str, Any]]:
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

    def delete_participants(
        self,
        survey_id: int,
        participant_ids: Sequence[int],
    ) -> List[Dict[str, Any]]:
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

    def _map_response_keys(
        self,
        survey_id: int,
        response_data: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Converts response keys to LimeSurvey's internal representation.

        Args:
            survey_id: The survey ID where the response belongs.
            response_data: The response mapping.

        Returns:
            A new dictionary with the keys mapped to the <SID>X<GID>X<QID> format.
        """
        qs = {q["title"]: q for q in self.list_questions(survey_id)}

        return {
            ("{sid}X{gid}X{qid}".format(**qs[key]) if key in qs else key): value
            for key, value in response_data.items()
        }

    def add_response(self, survey_id: int, response_data: Mapping[str, Any]) -> int:
        """Add a single response to a survey.

        Args:
            survey_id: Survey to add the response to.
            response_data: Single response as a mapping.

        Returns:
            ID of the new response.
        """
        # Transform question codes to the format LimeSurvey expects
        data = self._map_response_keys(survey_id, response_data)
        return int(self.__session.add_response(survey_id, data))

    def add_responses(
        self,
        survey_id: int,
        responses: Iterable[Mapping[str, Any]],
    ) -> List[int]:
        """Add multiple responses to a survey.

        Args:
            survey_id: Survey to add the response to.
            responses: Iterable of survey responses.

        Returns:
            IDs of the new responses.
        """
        ids = []
        for response in responses:
            response_id = self.add_response(survey_id, response)
            ids.append(response_id)
        return ids

    def delete_response(self, survey_id: int, response_id: int) -> Dict[str, str]:
        """Delete a response in a survey.

        Args:
            survey_id: ID of the survey the response belongs to.
            response_id: ID of the response to delete.

        Returns:
            Status message.
        """
        return self.__session.delete_response(survey_id, response_id)

    def delete_survey(self, survey_id: int) -> Dict[str, str]:
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
        token: Optional[str] = None,
        file_format: str = "json",
        language: Optional[str] = None,
        completion_status: str = "all",
        heading_type: str = "code",
        response_type: str = "short",
        from_response_id: Optional[int] = None,
        to_response_id: Optional[int] = None,
        fields: Optional[Sequence[str]] = None,
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
        else:
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

    def get_participant_properties(
        self,
        survey_id: int,
        query: Union[Dict[str, Any], int],
        properties: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
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

    def get_response_ids(
        self,
        survey_id: int,
        token: str,
    ) -> List[int]:
        """Find response IDs given a survey ID and a token.

        Args:
            survey_id: Survey to get responses from.
            token: Participant for which to get response IDs.

        Returns:
            A list of response IDs.
        """
        return self.__session.get_response_ids(survey_id, token)

    def _get_site_setting(self, setting_name: str) -> Any:
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

        Returns:
            The name of the theme.
        """
        return self._get_site_setting("defaulttheme")

    def get_site_name(self) -> str:
        """Get the site name.

        Returns:
            The name of the site.
        """
        return self._get_site_setting("sitename")

    def get_default_language(self) -> str:
        """Get the default site language.

        Returns:
            A string representing the language.
        """
        return self._get_site_setting("defaultlang")

    def get_available_languages(self) -> Optional[List[str]]:
        """Get the list of available languages.

        Returns:
            Either a list of strings for the available languages or None if there are
                no restrictions.
        """
        langs: str = self._get_site_setting("restrictToLanguages")

        return langs.split(" ") if langs else None

    def get_survey_properties(
        self,
        survey_id: int,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
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
        token: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Get a dictionary of files uploaded in a survey response.

        Args:
            survey_id: Survey for which to download files.
            token: Optional participant token to filter uploaded files.

        Returns:
            Dictionary with uploaded files metadata.

        >>> client.get_uploaded_files(12345)
        {
            '1234': {
                'meta': {
                    'title': 'one',
                    'comment': 'File One',
                    'name': 'file1.txt',
                    'filename': '1234',
                    'size': 48.046,
                    'ext': 'txt',
                    'question': {'title': 'G01Q01', 'qid': 1},
                    'index': 0
                },
                'content': <BASE64 content>
            }
        }
        """
        return self.__session.get_uploaded_files(survey_id, token)

    def download_files(
        self,
        directory: Union[str, Path],
        survey_id: int,
        token: Optional[str] = None,
    ) -> List[Path]:
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
        files_data = self.get_uploaded_files(survey_id, token=token)

        for file in files_data:
            metadata = files_data[file]["meta"]
            filepath = dirpath / metadata["filename"]
            filepaths.append(filepath)
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(files_data[file]["content"]))

        return filepaths

    def import_survey(
        self,
        file: BinaryIO,
        file_type: str = "lss",
        survey_name: Optional[str] = None,
        survey_id: Optional[int] = None,
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
        start: int = 0,
        limit: int = 10,
        unused: bool = False,
        attributes: Union[Sequence[str], bool] = False,
        conditions: Optional[Mapping[str, Any]] = {},
    ) -> List[Dict[str, Any]]:
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
            conditions,
        )

    def list_users(self) -> List[Dict[str, Any]]:
        """Get LimeSurvey users.

        Returns:
            List of users.
        """
        return self.__session.list_users()

    def list_questions(
        self,
        survey_id: int,
        group_id: Optional[int] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get questions in a survey, in a specific group or all.

        Args:
            survey_id: Survey.
            group_id: Question group.
            language: Retrieve question text, description, etc. in this language.

        Returns:
            List of participants with basic information.
        """
        return self.__session.list_questions(survey_id, group_id, language)

    def list_surveys(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all surveys or only those owned by a user.

        Args:
            username: Owner of the surveys to retrieve.

        Returns:
            List of surveys with basic information.
        """
        return self.__session.list_surveys(username)

    def list_survey_groups(
        self,
        username: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all survey groups or only those owned by a user.

        Args:
            username: Owner of the survey groups to retrieve.

        Returns:
            List of survey groups with basic information.
        """
        return self.__session.list_survey_groups(username)
