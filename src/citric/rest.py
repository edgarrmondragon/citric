"""REST API client implementation."""

from __future__ import annotations

from importlib import metadata
from typing import TYPE_CHECKING, Any

import requests

if TYPE_CHECKING:
    import sys
    from collections.abc import Mapping
    from types import TracebackType

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

__all__ = [
    "RESTClient",
]


class RESTClient:
    """LimeSurvey REST API client.

    Upon creation, retrieves a session ID that's used for authentication.

    .. warning::
       The REST API is still in early development, so the client is subject to changes.

    Args:
        url: LimeSurvey server URL. For example, ``http://www.yourdomain.com/rest/v1``.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A :py:class:`requests.Session <requests.Session>` object.

    .. versionadded:: NEXT_VERSION
    """

    USER_AGENT = f"citric/{metadata.version('citric')}"
    AUTH_ENDPOINT = "/rest/v1/auth"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: requests.Session | None = None,
    ) -> None:
        self.url = url
        self._session = requests_session or requests.session()
        self._session.headers["User-Agent"] = self.USER_AGENT
        self.__session_id: str | None = None

        self.authenticate(username=username, password=password)
        self._session.auth = self._auth

    @property
    def session_id(self) -> str | None:
        """Session ID."""
        return self.__session_id

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        """Set the session ID."""
        self.__session_id = value

    def authenticate(self, username: str, password: str) -> None:
        """Authenticate with the REST API.

        Args:
            username: LimeSurvey user name.
            password: LimeSurvey password.
        """
        response = self._session.post(
            url=f"{self.url}{self.AUTH_ENDPOINT}",
            json={
                "username": username,
                "password": password,
            },
        )
        response.raise_for_status()
        self.session_id = response.json()["token"]

    def refresh_token(self) -> None:
        """Refresh the session token."""
        response = self._session.put(url=f"{self.url}{self.AUTH_ENDPOINT}")
        response.raise_for_status()
        self.session_id = response.json()["token"]

    def close(self) -> None:
        """Delete the session."""
        response = self._session.delete(f"{self.url}{self.AUTH_ENDPOINT}")
        response.raise_for_status()
        self.session_id = None
        self._session.auth = None

    def _auth(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Authenticate with the REST API.

        This is an auth callable for
        :py:attr:`requests.Session.auth <requests.Session.auth>`.

        Args:
            request: Prepared request.

        Returns:
            The prepared request with the ``Authorization`` header set.
        """
        request.headers["Authorization"] = f"Bearer {self.session_id}"
        return request

    def make_request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,  # noqa: ANN401
    ) -> requests.Response:
        """Make a request to the REST API.

        Args:
            method: HTTP method.
            path: URL path.
            params: Query parameters.
            json: JSON data.

        Returns:
            Response.
        """
        response = self._session.request(
            method=method,
            url=f"{self.url}{path}",
            params=params,
            json=json,
        )
        response.raise_for_status()
        return response

    def __enter__(self: Self) -> Self:
        """Context manager for REST session.

        Returns:
            LimeSurvey REST client.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Safely exit a REST session.

        Args:
            exc_type: Exception class.
            exc_value: Exception instance.
            traceback: Error traceback.
        """
        self.close()

    def get_surveys(self) -> list[dict[str, Any]]:
        """Get all surveys.

        Returns:
            List of surveys.
        """
        response = self.make_request("GET", "/rest/v1/survey")
        return response.json()["surveys"]

    def get_survey_details(self, survey_id: int) -> dict[str, Any]:
        """Get survey details.

        Args:
            survey_id: Survey ID.

        Returns:
            Survey details.
        """
        response = self.make_request("GET", f"/rest/v1/survey-detail/{survey_id}")
        return response.json()["survey"]

    def patch_survey(
        self,
        survey_id: int,
        patch_operations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply RFC 6902-based patch operations to a survey.

        This method provides low-level access to the survey patch endpoint,
        allowing updates to any survey entity (questions, answers, groups, etc.).

        Args:
            survey_id: Survey ID.
            patch_operations: List of patch operations. Each operation should have:
                - entity: Entity type (e.g., "question", "questionAnswer", etc.)
                - op: Operation type (e.g., "update", "create", "delete")
                - id: Entity identifier (format varies by entity type)
                - props: Properties to update

        Returns:
            Patch operation result with operationsApplied and erronousOperations.

        Examples:
            >>> # Update multiple question answers at once
            >>> client.patch_survey(  # xdoctest: +SKIP
            ...     12345,
            ...     [
            ...         {
            ...             "entity": "questionAnswer",
            ...             "op": "update",
            ...             "id": {"aid": 15},
            ...             "props": {"sortOrder": 1000},
            ...         },
            ...         {
            ...             "entity": "questionAnswer",
            ...             "op": "update",
            ...             "id": {"aid": 16},
            ...             "props": {"sortOrder": 2000},
            ...         },
            ...     ],
            ... )
            {'operationsApplied': 2, 'erronousOperations': []}

        .. versionadded:: NEXT_VERSION
        """
        response = self.make_request(
            "PATCH",
            f"/rest/v1/survey-detail/{survey_id}",
            json={"patch": patch_operations},
        )
        return response.json()

    def update_survey_details(
        self,
        survey_id: int,
        **data: Any,
    ) -> dict[str, Any] | bool:
        """Update survey details.

        Args:
            survey_id: Survey ID.
            data: Survey details.

        Returns:
            Updated survey details.
        """
        return self.patch_survey(
            survey_id,
            [
                {
                    "entity": "survey",
                    "op": "update",
                    "id": survey_id,
                    "props": data,
                },
            ],
        )
