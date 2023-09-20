"""Unit tests for REST API client."""

from __future__ import annotations

import json
import typing as t

import pytest
import tinydb
from tinydb.table import Document
from werkzeug.wrappers import Response

from citric._rest import RESTClient

if t.TYPE_CHECKING:
    from pytest_httpserver import HTTPServer
    from werkzeug.wrappers import Request


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
def api_handler(backend: tinydb.TinyDB) -> t.Callable[[Request], Response]:
    """API handler."""

    def handler(request: Request) -> Response:
        if request.path.endswith("/rest/v1/survey"):
            surveys = backend.table("surveys")
            if request.method == "GET":
                return Response(
                    json.dumps({"surveys": surveys.all()}),
                    content_type="application/json",
                )

        if "/rest/v1/survey-detail" in request.path:
            surveys = backend.table("surveys")
            survey_id = int(request.path.split("/")[-1])
            if request.method == "GET":
                return Response(
                    json.dumps({"survey": surveys.get(doc_id=survey_id)}),
                    content_type="application/json",
                )

            if request.method == "PATCH":
                surveys.update_multiple(
                    [
                        (patch["props"], tinydb.where("sid") == patch["id"])
                        for patch in request.json["patch"]
                    ],
                )
                return Response(
                    json.dumps(True),  # noqa: FBT003
                    content_type="application/json",
                )

        return Response(status=400)

    return handler


def test_db(backend: tinydb.TinyDB):
    """Test DB."""
    surveys = backend.table("surveys")
    assert surveys.get(doc_id=12345)["sid"] == 12345


@pytest.fixture
def rest_client(
    username: str,
    password: str,
    httpserver: HTTPServer,
) -> RESTClient:
    """LimeSurvey REST API client."""
    httpserver.expect_request(
        "/rest/v1/session",
        method="POST",
        json={
            "username": username,
            "password": password,
        },
    ).respond_with_json('"my-session-id"')
    return RESTClient(httpserver.url_for("").rstrip("/"), username, password)


def test_get_surveys(
    backend: tinydb.TinyDB,
    rest_client: RESTClient,
    httpserver: HTTPServer,
    api_handler: t.Callable[[Request], Response],
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
    api_handler: t.Callable[[Request], Response],
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
    api_handler: t.Callable[[Request], Response],
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
    assert result is True

    surveys = backend.table("surveys")
    assert surveys.get(doc_id=12345)["anonymized"] is True
    assert surveys.get(doc_id=12345)["tokenLength"] == 10
