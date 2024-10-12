"""Unit tests for REST API client."""

from __future__ import annotations

import json
import typing as t

import pytest
import tinydb
from tinydb.table import Document
from werkzeug.wrappers import Response

from citric._rest import RESTClient  # noqa: PLC2701

if t.TYPE_CHECKING:
    import sys

    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request

    if sys.version_info >= (3, 10):
        from typing import TypeAlias  # noqa: ICN003
    else:
        from typing_extensions import TypeAlias

    APIHandler: TypeAlias = t.Callable[[Request], Response]


@pytest.fixture(scope="module")
def username() -> str:
    """LimeSurvey user name."""
    return "user"


@pytest.fixture(scope="module")
def password() -> str:
    """LimeSurvey password."""
    return "password"


@pytest.fixture(scope="module")
def backend() -> tinydb.database.Table:
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
        if request.path.endswith("/rest/v1/survey"):
            surveys = backend.table("surveys")
            if request.method == "GET":
                return Response(
                    json.dumps({"surveys": surveys.all()}),
                    content_type=content_type,
                )

        if "/rest/v1/survey-detail" in request.path:
            surveys = backend.table("surveys")
            survey_id = int(request.path.split("/")[-1])
            if request.method == "GET":
                return Response(
                    json.dumps({"survey": surveys.get(doc_id=survey_id)}),
                    content_type=content_type,
                )

            if request.method == "PATCH":
                surveys.update_multiple(
                    [
                        (patch["props"], tinydb.where("sid") == patch["id"])
                        for patch in request.json["patch"]  # type: ignore[index]
                    ],
                )
                return Response(
                    json.dumps(
                        {
                            "operationsApplied": len(request.json["patch"]),  # type: ignore[index]
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
) -> t.Generator[RESTClient, None, None]:
    """LimeSurvey REST API client."""
    httpserver.expect_request(
        "/rest/v1/session",
        method="POST",
        json={"username": username, "password": password},
    ).respond_with_json("my-session-id")
    httpserver.expect_request("/rest/v1/session", method="DELETE").respond_with_data("")

    with RESTClient(httpserver.url_for("").rstrip("/"), username, password) as client:
        yield client


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
