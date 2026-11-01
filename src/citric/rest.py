# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""REST API client implementation."""

from __future__ import annotations

__lazy_modules__ = {
    "citric.exceptions",
    "citric.transport._default",
    "http",
    "json",
    "threading",
    "uuid",
    "urllib.parse",
}

import http
import json as _json
import threading
import uuid
from importlib import metadata
from typing import TYPE_CHECKING, Any, Type, overload  # ruff: ignore[deprecated-import]
from urllib.parse import urlencode, urlsplit, urlunsplit

from citric.exceptions import LimeSurveyApiError
from citric.transport._constants import DEFAULT_TIMEOUT
from citric.transport._default import _transport_or_default

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping, Sequence
    from types import TracebackType
    from typing import IO, Literal, Self

    from citric.transport.protocol import HTTPResponse, HTTPTransport
    from citric.types import (
        RESTSurveyDetail,
        RESTSurveyFilesPage,
        RESTSurveyImportResult,
        RESTSurveyResponsesPage,
    )

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


def _quote_header_value(value: str) -> str:
    """Make a name or filename safe to use in a ``Content-Disposition`` header.

    Returns:
        The value with backslashes and double quotes escaped.

    Raises:
        ValueError: If the value contains CR or LF.
    """
    if "\r" in value or "\n" in value:
        msg = f"Invalid multipart field name or filename: {value!r}"
        raise ValueError(msg)
    return value.replace("\\", "\\\\").replace('"', '\\"')


class _MultipartBody:
    """A ``multipart/form-data`` body that streams its file contents.

    Iterating yields the body in chunks, and the length is known up front so that
    transports send a ``Content-Length`` header instead of chunked encoding.
    """

    _CHUNK_SIZE = 64 * 1024

    def __init__(
        self,
        form: Mapping[str, str],
        files: Mapping[str, tuple[str, bytes | IO[bytes]]],
    ) -> None:
        self.boundary = uuid.uuid4().hex
        self.content_type = f"multipart/form-data; boundary={self.boundary}"

        # Each item is either literal bytes or a (file, size) pair.
        self._items: list[bytes | tuple[IO[bytes], int]] = []
        for name, value in form.items():
            quoted = _quote_header_value(name)
            self._items.append(
                (
                    f"--{self.boundary}\r\n"
                    f'Content-Disposition: form-data; name="{quoted}"'
                    f"\r\n\r\n{value}\r\n"
                ).encode()
            )
        for name, (filename, content) in files.items():
            quoted = _quote_header_value(name)
            quoted_filename = _quote_header_value(filename)
            self._items.append(
                (
                    f"--{self.boundary}\r\n"
                    f'Content-Disposition: form-data; name="{quoted}"; '
                    f'filename="{quoted_filename}"\r\n'
                    "Content-Type: application/octet-stream\r\n\r\n"
                ).encode()
            )
            if isinstance(content, bytes):
                self._items.append(content)
            else:
                self._items.append((content, self._remaining(content)))
            self._items.append(b"\r\n")
        self._items.append(f"--{self.boundary}--\r\n".encode())

    @staticmethod
    def _remaining(file: IO[bytes]) -> int:
        """Get the number of bytes left to read from a seekable file.

        Returns:
            The number of remaining bytes.
        """
        start = file.tell()
        end = file.seek(0, 2)
        _ = file.seek(start)
        return end - start

    def __len__(self) -> int:
        return sum(
            len(item) if isinstance(item, bytes) else item[1] for item in self._items
        )

    def __iter__(self) -> Iterator[bytes]:
        for item in self._items:
            if isinstance(item, bytes):
                yield item
                continue

            file, size = item
            start = file.tell()
            remaining = size
            while remaining > 0:
                chunk = file.read(min(self._CHUNK_SIZE, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
            _ = file.seek(start)


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
        timeout: Seconds to wait to connect to the server, and then to receive each
            chunk of the response. Use ``None`` to defer to the transport's own
            default. Defaults to 300 seconds.

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

    .. version-added:: NEXT_VERSION
        The ``timeout`` parameter.
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
        timeout: float | None = DEFAULT_TIMEOUT,
    ) -> None:
        self.url: str = url
        self._timeout = timeout
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
        form: Mapping[str, str] | None = None,
        files: Mapping[str, tuple[str, bytes | IO[bytes]]] | None = None,
    ) -> HTTPResponse:
        """Make a request to the REST API.

        Args:
            method: HTTP method.
            path: URL path.
            params: Query parameters.
            json: JSON data.
            form: Text fields for a ``multipart/form-data`` body.
            files: Mapping of field name to ``(filename, content)`` for a
                ``multipart/form-data`` body. The content is either bytes or a
                seekable binary file, which is streamed.

        Returns:
            Response.

        Raises:
            ValueError: If ``json`` is combined with ``form`` or ``files``, or if a
                field name or filename contains a line break.

        .. versionchanged:: NEXT_VERSION
           Added the ``form`` and ``files`` parameters.
        """
        if json is not None and (form or files):
            msg = "'json' can't be combined with 'form' or 'files'"
            raise ValueError(msg)

        headers = (
            self._headers
            if path == self.AUTH_ENDPOINT and method == "POST"
            else self._auth_headers
        )
        body: str | _MultipartBody | None = None
        if json is not None:
            headers = {**headers, "Content-Type": "application/json"}
            body = _json.dumps(json)
        elif form or files:
            body = _MultipartBody(form or {}, files or {})
            headers = {
                **headers,
                "Content-Type": body.content_type,
                "Content-Length": str(len(body)),
            }

        url = f"{self.url}{path}"
        url = _encode_params(url, params) if params else url

        response = self._transport.request(
            method=method,
            url=url,
            data=body,
            headers=headers,
            timeout=self._timeout,
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

    def import_survey(
        self,
        file: IO[bytes],
        *,
        file_type: Literal["lss", "lsa", "txt", "tsv"] = "lss",
        group_strategy: Literal["default", "from_survey"] = "default",
        translate_links: bool = True,
    ) -> RESTSurveyImportResult:
        """Import a complete survey from a file.

        Args:
            file: Binary file object.
            file_type: Type of file. One of LSS, LSA, TXT and TSV.
            group_strategy: Whether to put the survey in the default survey group
                or the one defined in the file.
            translate_links: Whether to convert links to the old survey.

        Returns:
            The import result.

        .. note::
           The result is typed for LSS files. Other file types may return
           additional keys.

        .. minlimesurvey:: 7.8.0

        .. versionadded:: NEXT_VERSION
        """
        response = self.make_request(
            "POST",
            "/rest/v1/survey-import",
            form={
                "surveysgroup": group_strategy,
                "translinksfields": "1" if translate_links else "0",
            },
            files={"file": (f"survey.{file_type}", file)},
        )
        return response.json()

    @overload
    def get_survey_responses(
        self,
        survey_id: int,
        *,
        filters: Sequence[Mapping[str, Any]] | None = None,
        sort: Mapping[str, Any] | None = None,
        page_size: int | None = None,
        current_page: int | None = None,
        fields: Sequence[str] | None = None,
        language: str | None = None,
        unnest_files: Literal[False] = False,
    ) -> RESTSurveyResponsesPage: ...

    @overload
    def get_survey_responses(
        self,
        survey_id: int,
        *,
        filters: Sequence[Mapping[str, Any]] | None = None,
        sort: Mapping[str, Any] | None = None,
        page_size: int | None = None,
        current_page: int | None = None,
        fields: Sequence[str] | None = None,
        language: str | None = None,
        unnest_files: Literal[True],
    ) -> RESTSurveyFilesPage: ...

    def get_survey_responses(
        self,
        survey_id: int,
        *,
        filters: Sequence[Mapping[str, Any]] | None = None,
        sort: Mapping[str, Any] | None = None,
        page_size: int | None = None,
        current_page: int | None = None,
        fields: Sequence[str] | None = None,
        language: str | None = None,
        unnest_files: bool = False,
    ) -> RESTSurveyResponsesPage | RESTSurveyFilesPage:
        """Get one page of the responses of a survey.

        Args:
            survey_id: Survey ID.
            filters: Filters, each a mapping with ``key`` (response column names),
                ``filterMethod`` (e.g. ``equal`` or ``contain``) and ``value``.
            sort: Sort definition, as accepted by LimeSurvey.
            page_size: Number of responses per page. LimeSurvey defaults to 15.
            current_page: Zero-based page number.
            fields: Response columns to return. The columns LimeSurvey needs to
                describe each response, like ``id`` and ``submitdate``, are always
                included.
            language: Language of the question and answer texts. Defaults to the
                survey's base language.
            unnest_files: Whether to list the files of a single file upload
                column in ``fields``, one entry per file.

        Returns:
            The page of responses, or of files if ``unnest_files`` is set.

        .. note::
           The columns of each response depend on the survey, so they aren't typed.

        .. minlimesurvey:: 7.8.0

        .. versionadded:: NEXT_VERSION
        """
        page: dict[str, int] = {}
        if page_size is not None:
            page["pageSize"] = page_size
        if current_page is not None:
            page["currentPage"] = current_page

        body: dict[str, Any] = {
            "filters": filters,
            "sort": sort,
            "page": page or None,
            "fields": fields,
            "language": language,
            "unnestFiles": unnest_files or None,
        }
        response = self.make_request(
            "POST",
            f"/rest/v1/survey-responses/{survey_id}",
            json={key: value for key, value in body.items() if value is not None},
        )
        return response.json()
