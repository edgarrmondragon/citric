"""Test fixtures and mock helpers."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, ClassVar

import requests
from requests.adapters import BaseAdapter

if TYPE_CHECKING:
    from collections.abc import Mapping


class MailpitClient:
    """Mailpit API client."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    def get_all(self) -> dict:
        """Get all messages."""
        return requests.get(f"{self.base_url}/api/v1/messages", timeout=10).json()

    def delete(self) -> None:
        """Delete all messages."""
        requests.delete(
            f"{self.base_url}/api/v1/messages",
            timeout=10,
            params={"query": "after:2024/04/01"},
        )


class LimeSurveyMockAdapter(BaseAdapter):
    """Requests adapter that mocks LSRC2 API calls."""

    api_error_methods = ("__api_error",)
    status_error_methods = ("__status_error",)
    http_error_methods = ("__http_error",)
    ok_methods = ("__ok", "release_session_key")
    status_ok_methods = ("__status_ok", "activate_tokens", "delete_survey")

    session_key = "123456"
    status_ok: ClassVar[dict[str, Any]] = {"status": "OK"}
    rpc_interface = "json"

    ldap_session_key = "ldap-key"

    def _handle_json_response(
        self,
        method: str,
        params: list[Any],
        request_id: int,
    ) -> requests.Response:
        response = requests.Response()
        response.status_code = 200
        output: dict[str, Any] = {"result": None, "error": None, "id": request_id}

        if method in self.api_error_methods:
            output["error"] = "API Error!"
        elif method in self.status_error_methods:
            output["result"] = {"status": "Status Error!"}
        elif method in self.http_error_methods:
            response.status_code = 500
        elif method in self.ok_methods:
            output["result"] = "OK"
        elif method in self.status_ok_methods:
            output["result"] = self.status_ok
        elif method == "__bad_id":
            output["id"] = 2
        elif method == "get_session_key":
            output["result"] = (
                self.ldap_session_key if params[2] == "AuthLDAP" else self.session_key
            )
        elif method == "get_site_settings" and params[1] == "RPCInterface":
            output["result"] = self.rpc_interface

        response._content = json.dumps(output).encode()

        return response

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,  # noqa: FBT001, FBT002
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,  # noqa: FBT001, FBT002
        cert: bytes | str | tuple[bytes | str, bytes | str] | None = None,
        proxies: Mapping[str, str] | None = None,
    ):
        """Send a mocked request."""
        request_data = json.loads(request.body or "{}")
        method = request_data["method"]
        params = request_data["params"]
        request_id = request_data.get("id", 1)

        if method == "__disabled":
            response = requests.Response()
            response.status_code = 200
            return response

        if method == "__not_json":
            response = requests.Response()
            response.status_code = 200
            response._content = b"this is not json"
            return response

        return self._handle_json_response(method, params, request_id)

    def close(self) -> None:
        """Clean up adapter specific items."""
