# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Unit tests for REST API client."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import tinydb
import tinydb.storages
import tinydb.table
from tinydb.table import Document
from werkzeug.wrappers import Response

from citric.exceptions import LimeSurveyApiError
from citric.rest import RESTClient, _encode_params  # ruff: ignore[import-private-name]

if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import TypeAlias

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    APIHandler: TypeAlias = Callable[[Request], Response]


@pytest.fixture(scope="module")
def username() -> str:
    """LimeSurvey user name."""
    return "user"


@pytest.fixture(scope="module")
def password() -> str:
    """LimeSurvey password."""
    return "password"


@pytest.fixture(scope="module")
def backend() -> tinydb.table.Table:
    """TinyDB backend."""
    db = tinydb.TinyDB(storage=tinydb.storages.MemoryStorage)
    surveys = db.table("surveys")
    surveys.insert_multiple(
        [
            Document(
                {
                    "sid": 12345,
                    "active": True,
                    "anonymized": False,
                    "tokenLength": 5,
                },
                doc_id=12345,
            ),
            Document(
                {
                    "sid": 67890,
                    "active": True,
                    "anonymized": False,
                    "tokenLength": 5,
                },
                doc_id=67890,
            ),
        ],
    )
    return db


@pytest.fixture
def api_handler(backend: tinydb.TinyDB) -> APIHandler:
    """API handler."""
    content_type = "application/json"

    def handler(request: Request) -> Response:
        surveys = backend.table("surveys")

        if request.method == "GET":
            # A bodiless request must not claim a JSON body: LimeSurvey's REST
            # API 500s if it does, since it tries to decode the (empty) body.
            assert "Content-Type" not in request.headers

        if request.path.endswith("/rest/v1/survey") and request.method == "GET":
            return Response(
                json.dumps({"surveys": surveys.all()}),
                content_type=content_type,
            )

        if "/rest/v1/survey-detail" in request.path and request.method == "GET":
            survey_id = int(request.path.split("/")[-1])
            return Response(
                json.dumps({"survey": surveys.get(doc_id=survey_id)}),
                content_type=content_type,
            )

        if "/rest/v1/survey-detail" in request.path and request.method == "PATCH":
            assert request.headers.get("Content-Type") == "application/json"
            surveys.update_multiple(
                [
                    (patch["props"], tinydb.where("sid") == patch["id"])
                    for patch in request.json["patch"]
                ],
            )
            return Response(
                json.dumps(
                    {
                        "operationsApplied": len(request.json["patch"]),
                        "erronousOperations": [],
                    },
                ),
                content_type=content_type,
            )

        return Response(status=400)

    return handler


@pytest.fixture
def rest_client(
    username: str,
    password: str,
    httpserver: HTTPServer,
) -> Generator[RESTClient, None, None]:
    """LimeSurvey REST API client."""
    httpserver.expect_request(
        "/rest/v1/auth",
        method="POST",
        json={"username": username, "password": password},
    ).respond_with_json({"token": "my-session-id"})
    httpserver.expect_request("/rest/v1/auth", method="DELETE").respond_with_data("")

    with RESTClient(httpserver.url_for("").rstrip("/"), username, password) as client:
        yield client


def test_encode_params():
    """Test encoding of query parameters."""
    url = "https://example.com"
    assert _encode_params(url, {}) == url
    assert _encode_params(f"{url}?foo=bar", {}) == f"{url}?foo=bar"
    assert _encode_params(f"{url}?foo=bar", {"baz": "qux"}) == f"{url}?foo=bar&baz=qux"


def test_refresh_token(rest_client: RESTClient, httpserver: HTTPServer):
    """Test refreshing the token, a bodiless request."""

    def handler(request: Request) -> Response:
        assert "Content-Type" not in request.headers
        return Response(
            json.dumps({"token": "my-refreshed-session-id"}),
            content_type="application/json",
        )

    httpserver.expect_request(
        "/rest/v1/auth",
        method="PUT",
    ).respond_with_handler(handler)

    old_session_id = rest_client.session_id
    rest_client.refresh_token()
    assert rest_client.session_id == "my-refreshed-session-id"
    assert rest_client.session_id != old_session_id


def test_bad_request(
    backend: tinydb.TinyDB,
    rest_client: RESTClient,
    httpserver: HTTPServer,
    api_handler: APIHandler,
):
    """Test a bad request."""
    httpserver.expect_request(
        "/rest/v1/not-an-endpoint",
        method="GET",
    ).respond_with_handler(api_handler)

    with pytest.raises(
        LimeSurveyApiError,
        match="Request to LimeSurvey server failed with status 400",
    ):
        _ = rest_client.make_request("GET", "/rest/v1/not-an-endpoint")


def test_get_surveys(
    backend: tinydb.TinyDB,
    rest_client: RESTClient,
    httpserver: HTTPServer,
    api_handler: APIHandler,
):
    """Test getting surveys."""
    httpserver.expect_request(
        "/rest/v1/survey",
        method="GET",
    ).respond_with_handler(api_handler)

    assert rest_client.get_surveys() == backend.table("surveys").all()


def test_get_survey_details(
    backend: tinydb.TinyDB,
    rest_client: RESTClient,
    httpserver: HTTPServer,
    api_handler: APIHandler,
):
    """Test getting survey details."""
    httpserver.expect_request(
        "/rest/v1/survey-detail/12345",
        method="GET",
    ).respond_with_handler(api_handler)

    surveys = backend.table("surveys")
    assert rest_client.get_survey_details(survey_id=12345) == surveys.get(doc_id=12345)


def test_update_survey_details(
    backend: tinydb.TinyDB,
    rest_client: RESTClient,
    httpserver: HTTPServer,
    api_handler: APIHandler,
):
    """Test updating survey details."""
    httpserver.expect_request(
        "/rest/v1/survey-detail/12345",
        method="PATCH",
    ).respond_with_handler(api_handler)

    result = rest_client.update_survey_details(
        survey_id=12345,
        anonymized=True,
        tokenLength=10,
    )
    assert isinstance(result, dict)
    assert result["operationsApplied"] == 1
    assert result["erronousOperations"] == []

    surveys = backend.table("surveys")
    survey = surveys.get(doc_id=12345)
    assert isinstance(survey, Document)
    assert survey["anonymized"] is True
    assert survey["tokenLength"] == 10
