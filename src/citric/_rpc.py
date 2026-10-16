# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Transport-independent building blocks shared by the sync and async sessions."""

from __future__ import annotations

__lazy_modules__ = {
    "citric.exceptions",
    "http",
    "json",
    "random",
}

import http
import json
import logging
import random
from importlib import metadata
from typing import TYPE_CHECKING, Any

from citric.exceptions import (
    InvalidJSONResponseError,
    LimeSurveyApiError,
    LimeSurveyStatusError,
    ResponseMismatchError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from citric.transport.protocol import HTTPResponse
    from citric.types import RPCRequest, RPCResponse

GET_SESSION_KEY = "get_session_key"
USER_AGENT = f"citric/{metadata.version('citric')}"

logger: logging.Logger = logging.getLogger("citric.session")


def needs_session_key(method: str) -> bool:
    """Whether an RPC method requires a session key as its first parameter.

    Args:
        method: Name of the RPC method.

    Returns:
        ``False`` for ``get_session_key`` and ``system.*`` methods, else ``True``.
    """
    return not (method == GET_SESSION_KEY or method.startswith("system."))


def new_request(method: str, params: tuple[Any, ...]) -> RPCRequest:
    """Build an RPC request payload with a random request ID.

    Args:
        method: Name of the RPC method.
        params: Positional arguments of the RPC method.

    Returns:
        The request payload.
    """
    return {
        "method": method,
        "params": [*params],
        "id": random.randint(1, 999_999),  # ruff: ignore[suspicious-non-cryptographic-random-usage]
    }


def encode_request(payload: RPCRequest, encoder: type[json.JSONEncoder]) -> str:
    """Serialize an RPC request payload.

    Args:
        payload: The request payload.
        encoder: The JSON encoder class.

    Returns:
        The JSON body.
    """
    return json.dumps(payload, cls=encoder)


def request_headers() -> Mapping[str, str]:
    """HTTP headers of every RPC request.

    Returns:
        The headers.
    """
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "User-Agent": USER_AGENT,
    }


def parse_response(res: HTTPResponse, payload: RPCRequest) -> RPCResponse:
    """Check and decode the HTTP response to an RPC request.

    Args:
        res: The HTTP response.
        payload: The request that was sent.

    Returns:
        The decoded RPC response.

    Raises:
        LimeSurveyApiError: If the server responds with an error HTTP status code.
        InvalidJSONResponseError: If the response is not valid JSON.
    """
    if res.status_code >= http.HTTPStatus.BAD_REQUEST:
        msg = f"Request to LimeSurvey server failed with status {res.status_code}"
        raise LimeSurveyApiError(msg)

    data: RPCResponse

    try:
        data = res.json()
    except ValueError as e:
        raise InvalidJSONResponseError from e

    logger.info("Invoked RPC method %s with ID %d", payload["method"], payload["id"])
    validate_rpc_response(payload["id"], data)

    return data


def validate_rpc_response(request_id: int, data: RPCResponse) -> None:
    """Raise if an RPC response doesn't match the request, or carries an error.

    Args:
        request_id: ID of the request.
        data: The decoded RPC response.

    Raises:
        ResponseMismatchError: If the response ID doesn't match the request ID.
        LimeSurveyApiError: If the response carries an error.
    """
    if (response_id := data["id"]) != request_id:
        msg = f"Response ID {response_id} does not match request ID {request_id}"
        raise ResponseMismatchError(msg)

    if (error := data["error"]) is not None:
        raise LimeSurveyApiError(error)


def check_result_status(result: Any) -> None:  # ruff: ignore[any-type]
    """Raise if an RPC result is a dict with a status other than ``OK``.

    Args:
        result: The RPC result.

    Raises:
        LimeSurveyStatusError: If the result has a status other than ``OK``.
    """
    if isinstance(result, dict) and result.get("status") not in {"OK", None}:
        raise LimeSurveyStatusError(
            result["status"],
            error_code=result.get("error_code"),
        )
