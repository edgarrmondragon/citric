from __future__ import annotations

import typing as t
from importlib import metadata

import requests


class RESTClient:
    """LimeSurvey REST API client.

    Upon creation, retrieves a session ID that's used for authentication.

    .. warning::
       The REST API is still in development and not yet stable, so the client is
       subject to changes.

    Args:
        url: LimeSurvey server URL. For example, ``http://www.yourdomain.com/rest/v1.``.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        requests_session: A :py:class:`requests.Session <requests.Session>` object.

    .. versionadded:: NEXT_VERSION
       Support the REST API.
    """

    USER_AGENT = f"citric/{metadata.version('citric')}"

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        requests_session: requests.Session | None = None,
    ) -> None:
        """Create a LimeSurvey REST session."""
        self.url = url
        self._session = requests_session or requests.session()
        self._session.headers["User-Agent"] = self.USER_AGENT

        self.__session_id = self._authenticate(
            username=username,
            password=password,
        )
        self._session.auth = self._auth

    def _authenticate(self, username: str, password: str) -> str:
        """Authenticate with the REST API.

        Args:
            username: LimeSurvey user name.
            password: LimeSurvey password.

        Returns:
            Session ID.
        """
        response = self._session.post(
            url=f"{self.url}/rest/v1/session",
            json={
                "username": username,
                "password": password,
            },
        )
        response.raise_for_status()
        return response.json()

    def _auth(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Authenticate with the REST API.

        This is an auth callable for
        :py:attr:`requests.Session.auth <requests.Session.auth>`.

        Args:
            request: Prepared request.

        Returns:
            The prepared request with the ``Authorization`` header set.
        """
        request.headers["Authorization"] = f"Bearer {self.__session_id}"
        return request

    def get_surveys(self) -> list[dict[str, t.Any]]:
        """Get all surveys.

        Returns:
            List of surveys.
        """
        response = self._session.get(url=f"{self.url}/rest/v1/survey")
        response.raise_for_status()
        return response.json()["surveys"]
