# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""REST API client implementation."""

from __future__ import annotations

__lazy_modules__ = {
    "citric.exceptions",
    "citric.transport._default",
    "http",
    "json",
    "threading",
    "urllib.parse",
}

import http
import json as _json
import threading
from importlib import metadata
from typing import TYPE_CHECKING, Any, Type  # ruff: ignore[deprecated-import]
from urllib.parse import urlencode, urlsplit, urlunsplit

from citric.exceptions import LimeSurveyApiError
from citric.transport._default import _transport_or_default

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType
    from typing import Self

    from citric.transport.protocol import HTTPResponse, HTTPTransport
    from citric.types import RESTSurveyDetail

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

    Retrieves a session ID, used for authentication, the first time it is needed.
    Creating a client doesn't contact the server.

    .. warning::
       The REST API is still in early development, so the client is subject to changes.

    Args:
        url: LimeSurvey server URL. For example, ``http://www.yourdomain.com/rest/v1``.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        transport: An HTTP transport implementing
            :class:`~citric.transport.protocol.HTTPTransport`, e.g. a
            :py:class:`requests.Session <requests.Session>` or
            :class:`~citric.transport.httpx2.Httpx2Transport`. Defaults to a new
            :py:class:`requests.Session <requests.Session>`.
        requests_session: Deprecated alias of ``transport``.

    .. versionadded:: 0.10.0.post1

    .. version-changed:: NEXT_VERSION
        Authentication is deferred until the session ID is first needed, instead of
        happening on creation. Credentials are kept in memory until then, or until
        the client is closed. Deferred authentication is thread-safe: concurrent
        users of a new client authenticate only once.

    .. versionchanged:: NEXT_VERSION
        The ``requests_session`` parameter was deprecated in favor of its alias
        ``transport``. It also now accepts any object implementing
        :class:`~citric.transport.protocol.HTTPTransport`, not just
        :py:class:`requests.Session <requests.Session>`.

    .. deprecated:: NEXT_VERSION
        The ``requests_session`` parameter, use ``transport`` instead.
    """

    USER_AGENT = f"citric/{metadata.version('citric')}"
    AUTH_ENDPOINT = "/rest/v1/auth"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        transport: HTTPTransport | None = None,
        requests_session: HTTPTransport | None = None,
    ) -> None:
        self.url: str = url
        self._transport = _transport_or_default(transport, requests_session)
        self.__lock = threading.RLock()
        self.__closed: bool = False
        self.__session_id: str | None = None
        self._headers = {
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        self.__credentials: tuple[str, str] | None = (username, password)

    @property
    def _auth_headers(self) -> dict[str, str]:
        assert self.session_id is not None  # ruff: ignore[assert]
        return {
            **self._headers,
            "Authorization": f"Bearer {self.session_id}",
        }

    @property
    def session_id(self) -> str | None:
        """Session ID.

        The first access authenticates with the server.
        """
        with self.__lock:
            if self.__credentials is not None:
                self.authenticate(*self.__credentials)
            return self.__session_id

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        """Set the session ID, replacing any pending deferred authentication."""
        with self.__lock:
            self.__credentials = None
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
        with self.__lock:
            response = self.make_request(
                "POST",
                path=self.AUTH_ENDPOINT,
                json={"username": username, "password": password},
            )
            self.session_id = response.json()["token"]

    def refresh_token(self) -> None:
        """Refresh the session token."""
        with self.__lock:
            response = self.make_request("PUT", path=self.AUTH_ENDPOINT)
            self.session_id = response.json()["token"]

    def close(self) -> None:
        """Delete the session, if one was created.

        Closing a client more than once has no effect.
        """
        # Wait for an in-flight deferred connection so its session gets deleted
        with self.__lock:
            if self.__closed:
                return

            self.__credentials = None

            try:
                if self.__session_id is not None:
                    _ = self.make_request("DELETE", self.AUTH_ENDPOINT)
            finally:
                self._transport.close()
                self.session_id = None
                self.__closed = True

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
        headers = (
            self._headers
            if path == self.AUTH_ENDPOINT and method == "POST"
            else self._auth_headers
        )
        if json is not None:
            headers = {**headers, "Content-Type": "application/json"}

        url = f"{self.url}{path}"
        url = _encode_params(url, params) if params else url

        response = self._transport.request(
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

    def get_survey_details(self, survey_id: int) -> RESTSurveyDetail:
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
