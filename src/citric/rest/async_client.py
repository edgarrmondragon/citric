"""REST API client implementation."""

from __future__ import annotations

import typing as t

import httpx

from citric._util import get_citric_user_agent

if t.TYPE_CHECKING:
    import sys
    from types import TracebackType

    if sys.version_info >= (3, 11):
        from typing import Self  # noqa: ICN003
    else:
        from typing_extensions import Self


class AsyncRESTClient:
    """Async LimeSurvey REST API client.

    .. warning::
       The REST API is still in early development, so the client is subject to changes.

    Args:
        url: LimeSurvey server URL. For example, ``http://www.yourdomain.com/rest/v1``.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        http_client: A :py:class:`httpx.AsyncClient <requests.Session>` object.

    .. versionadded:: NEXT_VERSION
    """

    USER_AGENT = get_citric_user_agent()

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: httpx.AsyncClient | None = None,
    ) -> None:
        """Create a LimeSurvey REST session."""
        self.url = url
        self.username = username
        self.password = password
        self._session = requests_session or httpx.AsyncClient()
        self._session.headers["User-Agent"] = self.USER_AGENT
        self._session_id: str | None = None

    async def authenticate(self, username: str, password: str) -> None:
        """Authenticate with the REST API.

        Args:
            username: LimeSurvey user name.
            password: LimeSurvey password.
        """
        response = await self._session.post(
            url=f"{self.url}/rest/v1/session",
            json={
                "username": username,
                "password": password,
            },
        )
        response.raise_for_status()
        self._session_id = response.json()

    async def close(self) -> None:
        """Delete the session."""
        response = await self._session.delete(f"{self.url}/rest/v1/session")
        response.raise_for_status()
        self._session_id = None
        self._session.auth = None

    def _auth(self, request: httpx.Request) -> httpx.Request:
        """Authenticate with the REST API.

        This is an auth callable for
        :py:attr:`requests.Session.auth <requests.Session.auth>`.

        Args:
            request: Prepared request.

        Returns:
            The prepared request with the ``Authorization`` header set.
        """
        request.headers["Authorization"] = f"Bearer {self._session_id}"
        return request

    async def make_request(
        self,
        method: str,
        path: str,
        *,
        params: t.Mapping[str, t.Any] | None = None,
        json: t.Any | None = None,  # noqa: ANN401
    ) -> httpx.Response:
        """Make a request to the REST API.

        Args:
            method: HTTP method.
            path: URL path.
            params: Query parameters.
            json: JSON data.

        Returns:
            Response.
        """
        response = await self._session.request(
            method=method,
            url=f"{self.url}{path}",
            params=params,
            json=json,
        )
        response.raise_for_status()
        return response

    async def __aenter__(self: Self) -> Self:
        """Context manager for REST session.

        Returns:
            LimeSurvey REST client.
        """
        await self.authenticate(
            username=self.username,
            password=self.password,
        )
        self._session.auth = self._auth
        return self

    async def __aexit__(
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
        await self.close()

    async def get_surveys(self) -> list[dict[str, t.Any]]:
        """Get all surveys.

        Returns:
            List of surveys.
        """
        response = await self.make_request("GET", "/rest/v1/survey")
        return response.json()["surveys"]

    async def get_survey_details(self, survey_id: int) -> dict[str, t.Any]:
        """Get survey details.

        Args:
            survey_id: Survey ID.

        Returns:
            Survey details.
        """
        response = await self.make_request("GET", f"/rest/v1/survey-detail/{survey_id}")
        return response.json()["survey"]

    async def update_survey_details(
        self,
        survey_id: int,
        **data: t.Any,
    ) -> bool:
        """Update survey details.

        Args:
            survey_id: Survey ID.
            data: Survey details.

        Returns:
            Updated survey details.
        """
        response = await self.make_request(
            "PATCH",
            f"/rest/v1/survey-detail/{survey_id}",
            json={
                "patch": [
                    {
                        "entity": "survey",
                        "op": "update",
                        "id": survey_id,
                        "props": data,
                    },
                ],
            },
        )
        return response.json()
