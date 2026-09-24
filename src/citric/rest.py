# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""REST API client implementation."""

from __future__ import annotations

__lazy_modules__ = {
    "citric.exceptions",
    "http",
    "json",
    "requests",
}

import http
import json as _json
from importlib import metadata
from typing import TYPE_CHECKING, Any, Type  # ruff: ignore[deprecated-import]
from urllib.parse import urlencode, urlsplit, urlunsplit

import requests

from citric.exceptions import LimeSurveyApiError

if TYPE_CHECKING:
    import sys
    from collections.abc import Mapping
    from types import TracebackType

    from citric.transport.protocol import HTTPResponse, HTTPTransport

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

__all__ = [
    "RESTClient",
]


def _encode_params(url: str, params: Mapping[str, Any]) -> str:
    if not params:
        return url

    split = urlsplit(url)
    query = urlencode(params, doseq=True)
    if split.query:
        query = f"{split.query}&{query}"

    return urlunsplit(split._replace(query=query))


class RESTClient:
    """LimeSurvey REST API client.

    Upon creation, retrieves a session ID that's used for authentication.

    .. warning::
       The REST API is still in early development, so the client is subject to changes.

    Args:
        url: LimeSurvey server URL. For example, ``http://www.yourdomain.com/rest/v1``.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: An HTTP transport implementing
            :class:`~citric.transport.protocol.HTTPTransport`, e.g. a
            :py:class:`requests.Session <requests.Session>` or
            :class:`~citric.transport.httpx2.Httpx2Transport`. Defaults to a new
            :py:class:`requests.Session <requests.Session>`.

    .. versionadded:: 0.10.0.post1
    """

    USER_AGENT = f"citric/{metadata.version('citric')}"
    AUTH_ENDPOINT = "/rest/v1/auth"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: HTTPTransport | None = None,
    ) -> None:
        self.url: str = url
        self._session = (
            requests_session if requests_session is not None else requests.session()
        )
        self.__session_id: str | None = None
        self._headers = {
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        self.authenticate(username=username, password=password)

    @property
    def _auth_headers(self) -> dict[str, str]:
        assert self.session_id is not None  # ruff: ignore[assert]
        return {
            **self._headers,
            "Authorization": f"Bearer {self.session_id}",
        }

    @property
    def session_id(self) -> str | None:
        """Session ID."""
        return self.__session_id

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        """Set the session ID."""
        self.__session_id = value

    @staticmethod
    def _raise_for_status(r: HTTPResponse) -> None:
        if r.status_code >= http.HTTPStatus.BAD_REQUEST:
            msg = f"Request to LimeSurvey server failed with status {r.status_code}"
            raise LimeSurveyApiError(msg)

    def authenticate(self, username: str, password: str) -> None:
        """Authenticate with the REST API.

        Args:
            username: LimeSurvey user name.
            password: LimeSurvey password.
        """
        response = self._session.request(
            method="POST",
            url=f"{self.url}{self.AUTH_ENDPOINT}",
            data=_json.dumps({"username": username, "password": password}),
            headers={**self._headers, "Content-Type": "application/json"},
        )
        self._raise_for_status(response)
        self.session_id = response.json()["token"]

    def refresh_token(self) -> None:
        """Refresh the session token."""
        response = self._session.request(
            method="PUT",
            url=f"{self.url}{self.AUTH_ENDPOINT}",
            headers=self._auth_headers,
        )
        self._raise_for_status(response)
        self.session_id = response.json()["token"]

    def close(self) -> None:
        """Delete the session."""
        if self.session_id is None:
            return

        try:
            response = self._session.request(
                method="DELETE",
                url=f"{self.url}{self.AUTH_ENDPOINT}",
                headers=self._auth_headers,
            )
            self._raise_for_status(response)
        finally:
            self._session.close()
            self.session_id = None

    def make_request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,  # ruff: ignore[any-type]
    ) -> HTTPResponse:
        """Make a request to the REST API.

        Args:
            method: HTTP method.
            path: URL path.
            params: Query parameters.
            json: JSON data.

        Returns:
            Response.
        """
        headers = self._auth_headers
        if json is not None:
            headers = {**headers, "Content-Type": "application/json"}

        url = f"{self.url}{path}"
        url = _encode_params(url, params) if params else url

        response = self._session.request(
            method=method,
            url=url,
            data=_json.dumps(json) if json is not None else None,
            headers=headers,
        )
        self._raise_for_status(response)
        return response

    def __enter__(self: Self) -> Self:
        """Context manager for REST session.

        Returns:
            LimeSurvey REST client.
        """
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,  # ruff: ignore[non-pep585-annotation]
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
            Patch operation result with operationsApplied.

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
            {'operationsApplied': 2}

        .. versionadded:: 2.0.0
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
