"""Python API."""

import base64
import enum
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
)
from citric.session import Session


class ImportSurveyType(str, enum.Enum):
    """Survey file type."""

    LSS = "lss"
    CSV = "csv"
    TXT = "txt"
    LSA = "lsa"


class ResponsesExportTFormat(str, enum.Enum):
    """Responses export type."""

    PDF = "pdf"
    CSV = "csv"
    XLS = "xls"
    DOC = "doc"
    JSON = "json"


class SurveyCompletionStatus(str, enum.Enum):
    """Survey completion status values."""

    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    ALL = "all"


class HeadingType(str, enum.Enum):
    """Types of heading in responses export."""

    CODE = "code"
    FULL = "full"
    ABBREVIATED = "abbreviated"


class ResponseType(str, enum.Enum):
    """Types of responses in export."""

    LONG = "long"
    SHORT = "short"


class API:
    """Python API.

    Offers explicit wrappers for RPC methods and simplifies common worflows.

    Args:
        session: A LSRPC2 API authenticated session.
    """

    def __init__(self, session: Session) -> None:  # noqa: ANN101
        """Create a LimeSurvey Python API."""
        self.__session = session

    @property
    def session(self) -> Session:  # noqa: ANN101
        """RPC session."""
        return self.__session

    def activate_survey(self, survey_id: int) -> Dict[str, Any]:  # noqa: ANN101
        """Activate a survey.

        Args:
            survey_id: ID of survey to be activated.

        Returns:
            Status and plugin feedback.
        """
        return self.__session.activate_survey(survey_id)

    def activate_tokens(
        self, survey_id: int, attributes: Optional[List[str]] = None,  # noqa: ANN101
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
        self,  # noqa: ANN101
        survey_id: int,
        participant_data: Sequence[Mapping[str, Any]],
        create_tokens: bool = True,
    ) -> Dict[str, str]:
        """Add participants to a survey.

        Args:
            survey_id: Survey to add participants to.
            participant_data: Information to create participants with.
            create_tokens: Whether to create the participants with tokens.

        Returns:
            Information of newly created participants.
        """
        return self.__session.add_participants(
            survey_id, participant_data, create_tokens,
        )

    def add_response(
        self, survey_id: int, response_data: Mapping[str, Any],  # noqa: ANN101
    ) -> str:
        """Add a single response to a survey.

        Args:
            survey_id: Survey to add the response to.
            response_data: Single response as a mapping.

        Returns:
            ID of the new response.
        """
        return self.__session.add_response(survey_id, response_data)

    def add_responses(
        self, survey_id: int, responses: Iterable[Mapping[str, Any]],  # noqa: ANN101
    ) -> List[str]:
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

    def delete_survey(self, survey_id: int) -> Dict[str, str]:  # noqa: ANN101
        """Delete a survey.

        Args:
            survey_id: Survey to delete.

        Returns:
            Status message.
        """
        return self.__session.delete_survey(survey_id)

    def export_responses(
        self,  # noqa: ANN101
        file_object: BinaryIO,
        survey_id: int,
        file_format: ResponsesExportTFormat,
        language: Optional[str] = None,
        completion_status: SurveyCompletionStatus = SurveyCompletionStatus.ALL,
        heading_type: HeadingType = HeadingType.CODE,
        response_type: ResponseType = ResponseType.SHORT,
        from_response_id: Optional[int] = None,
        to_response_id: Optional[int] = None,
        fields: Optional[Sequence[str]] = None,
    ) -> int:
        """Export responses to a file-like object.

        Args:
            file_object: File-like object to store the results.
            survey_id: Survey to add the response to.
            file_format: Type of export. One of PDF, CSV, XLS, DOC or JSON.
            language: Export responses made to this language version of the survey.
            completion_status: Incomplete, complete or all.
            heading_type: Use response codes, long or abbreviated titles.
            response_type: Export long or short text responses.
            from_response_id: First response to export.
            to_response_id: Last response to export.
            fields: Which response fields to export. If none, exports all fields.

        Returns:
            Number of bytes written to file.
        """
        return file_object.write(
            base64.b64decode(
                self.__session.export_responses(
                    survey_id,
                    file_format,
                    language,
                    completion_status,
                    heading_type,
                    response_type,
                    from_response_id,
                    to_response_id,
                    fields,
                )
            )
        )

    def export_responses_by_token(
        self,  # noqa: ANN101
        file_object: BinaryIO,
        survey_id: int,
        file_format: ResponsesExportTFormat,
        token: str,
        language: Optional[str] = None,
        completion_status: SurveyCompletionStatus = SurveyCompletionStatus.ALL,
        heading_type: HeadingType = HeadingType.CODE,
        response_type: ResponseType = ResponseType.SHORT,
        from_response_id: Optional[int] = None,
        to_response_id: Optional[int] = None,
        fields: Optional[Sequence[str]] = None,
    ) -> int:
        """Export responses to a file-like object.

        Args:
            file_object: File-like object to store the results.
            survey_id: Survey to add the response to.
            file_format: Type of export. One of PDF, CSV, XLS, DOC or JSON.
            token: The token for which responses needed.
            language: Export responses made to this language version of the survey.
            completion_status: Incomplete, complete or all.
            heading_type: Use response codes, long or abbreviated titles.
            response_type: Export long or short text responses.
            from_response_id: First response to export.
            to_response_id: Last response to export.
            fields: Which response fields to export. If none, exports all fields.

        Returns:
            Number of bytes written to file.
        """
        return file_object.write(
            base64.b64decode(
                self.__session.export_responses(
                    survey_id,
                    file_format,
                    language,
                    completion_status,
                    heading_type,
                    response_type,
                    from_response_id,
                    to_response_id,
                    fields,
                )
            )
        )

    def get_participant_properties(
        self,  # noqa: ANN101
        survey_id: int,
        token: str,
        properties: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Get properties a single survey participant.

        Args:
            survey_id: Survey to get participants properties.
            token: Participants' tokens to retrieve.
            properties: Which participant properties to retrieve.

        Returns:
            List of participants properties.
        """
        return self.__session.get_participant_properties(survey_id, token, properties)

    def get_survey_properties(
        self, survey_id: int, properties: Optional[List[str]] = None,  # noqa: ANN101
    ) -> Dict[str, Any]:
        """Get properties of a survey.

        Args:
            survey_id: Survey to get properties.
            properties: Which survey properties to retrieve. If none, gets all fields.

        Returns:
            Dictionary of survey properties.
        """
        return self.__session.get_survey_properties(survey_id, properties)

    def import_survey(
        self,  # noqa: ANN101
        filepath: Union[Path, str],
        file_type: ImportSurveyType = ImportSurveyType.LSS,
        survey_name: Optional[str] = None,
        survey_id: Optional[int] = None,
    ) -> int:
        """Import survey from a file.

        Create a new survey from an exported LSS, CSV, TXT or LSA file.

        Args:
            filepath: Path to the file.
            file_type: Type of file. One of LSS, CSV, TXT and LSA.
            survey_name: Override the new survey name.
            survey_id: Desired ID of the new survey. A different ID will be used if
                there is already a survey with this ID.

        Returns:
            The ID of the new survey.
        """
        with open(filepath, "rb") as file:
            contents = base64.b64encode(file.read()).decode()
            return self.__session.import_survey(contents, file_type)

    def list_participants(
        self,  # noqa: ANN101
        survey_id: int,
        start: int = 0,
        limit: int = 10,
        unused: bool = False,
        attributes: Optional[Sequence[str]] = None,
        conditions: Optional[Mapping[str, Any]] = None,
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
            survey_id, start, limit, unused, attributes, conditions,
        )

    def list_questions(
        self,  # noqa: ANN101
        survey_id: int,
        group_id: Optional[int] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get question in a survey.

        Args:
            survey_id: Survey.
            group_id: Question group.
            language: Retrieve question text, description, etc. in this language.

        Returns:
            List of participants with basic information.
        """
        return self.__session.list_questions(survey_id, group_id, language)

    def list_surveys(
        self, username: Optional[str] = None,  # noqa: ANN101
    ) -> List[Dict[str, Any]]:
        """Get all surveys or only those owned by a user.

        Args:
            username: Owner of the surveys to retrieve.

        Returns:
            List of surveys with basic information.
        """
        return self.__session.list_surveys(username)
