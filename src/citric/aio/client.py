# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Python async API client."""

from __future__ import annotations

__lazy_modules__ = {
    "asyncio",
    "citric.aio.session",
    "pathlib",
}

import asyncio
import base64
import io
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from citric.aio._client_methods import AsyncClientMethods
from citric.aio.session import AsyncSession

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Sequence
    from os import PathLike
    from types import TracebackType
    from typing import Self

    from citric import enums, types
    from citric.aio.transport.protocol import AsyncHTTPTransport

__all__ = ["AsyncClient"]


class AsyncClient(AsyncClientMethods):
    """Asynchronous LimeSurvey RemoteControl 2 API client.

    The async counterpart of :class:`citric.client.Client`: its methods have the same
    names and parameters, but are coroutines. Closing the client is done with
    :meth:`aclose`, and the client is an async context manager.

    .. note::

       The async client only supports LimeSurvey 7.0 and later. Older servers aren't
       tested, and responses are always keyed by ``Q<question ID>`` fieldnames. Use
       :class:`citric.client.Client` for older servers.

    Args:
        url: LimeSurvey Remote Control endpoint.
        username: LimeSurvey user name.
        password: LimeSurvey password.
        transport: An HTTP transport implementing
            :class:`~citric.aio.transport.protocol.AsyncHTTPTransport`. Defaults to a
            new :class:`~citric.aio.transport.httpx2.AsyncHttpx2Transport`.
        auth_plugin: Name of the :ls_manual:`plugin <Authentication_plugins>` to use for
            authentication. For example,
            :ls_manual:`AuthLDAP <Authentication_plugins#LDAP>`. Defaults to using the
            :ls_manual:`internal database <Authentication_plugins#Internal_database>`
            (``"Authdb"``).

    .. versionadded:: NEXT_VERSION
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        *,
        transport: AsyncHTTPTransport | None = None,
        auth_plugin: str = "Authdb",
    ) -> None:
        self.__session = self._get_rpc_session(
            url=url,
            username=username,
            password=password,
            auth_plugin=auth_plugin,
            transport=transport,
        )

    def _get_rpc_session(  # ruff: ignore[no-self-use]
        self,
        *,
        url: str,
        username: str,
        password: str,
        auth_plugin: str = "Authdb",
        transport: AsyncHTTPTransport | None = None,
    ) -> AsyncSession:
        """Get the RPC session.

        Returns:
            The RPC session for this client.
        """
        return AsyncSession(
            url,
            username,
            password,
            auth_plugin=auth_plugin,
            transport=transport,
        )

    @property
    @override
    def session(self) -> AsyncSession:
        """Low-level RPC session."""
        return self.__session

    async def aclose(self) -> None:
        """Close client session."""
        await self.session.aclose()

    async def __aenter__(self: Self) -> Self:
        """Create client context.

        Returns:
            Client instance.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Safely exit the client context."""
        await self.aclose()

    @override
    async def _fieldname_from_question(
        self, question: types.QuestionsListElement
    ) -> str:
        # LimeSurvey 7+ names response fields after the question ID only
        return f"Q{question['qid']}"

    async def save_responses(  # ruff: ignore[too-many-arguments]
        self,
        filename: PathLike[str],
        survey_id: int,
        *,
        token: str | None = None,
        file_format: str = "json",
        language: str | None = None,
        completion_status: str = "all",
        heading_type: str = "code",
        response_type: str = "short",
        from_response_id: int | None = None,
        to_response_id: int | None = None,
        fields: Sequence[str] | None = None,
        additional_options: types.ExportAdditionalOptions | None = None,
    ) -> int:
        """Save responses to a file.

        The file is written in a worker thread, so the event loop isn't blocked.

        Args:
            filename: Target file path.
            survey_id: Survey from which responses should be exported.
            token: Optional participant token to get responses for.
            file_format: Type of export. One of PDF, CSV, XLS, DOC or JSON.
            language: Export responses made to this language version of the survey.
            completion_status: Incomplete, complete or all.
            heading_type: Use response codes, long or abbreviated titles.
            response_type: Export long or short text responses.
            from_response_id: First response to export.
            to_response_id: Last response to export.
            fields: Which response fields to export. If none, exports all fields.
            additional_options: Dictionary of additional options to format the export.

        Returns:
            Bytes length written to file.
        """
        content = await self.export_responses(
            survey_id,
            token=token,
            file_format=file_format,
            language=language,
            completion_status=completion_status,
            heading_type=heading_type,
            response_type=response_type,
            from_response_id=from_response_id,
            to_response_id=to_response_id,
            fields=fields,
            additional_options=additional_options,
        )
        return await asyncio.to_thread(Path(filename).write_bytes, content)

    async def save_statistics(
        self,
        filename: PathLike[str],
        survey_id: int,
        *,
        file_format: str | enums.StatisticsExportFormat = "pdf",
        language: str | None = None,
        graph: bool = False,
        group_ids: list[int] | None = None,
    ) -> int:
        """Save survey statistics to a file.

        The file is written in a worker thread, so the event loop isn't blocked.

        Args:
            filename: Target file path.
            survey_id: ID of the Survey.
            file_format: Type of documents the exported statistics should be.
                Defaults to "pdf".
            language: Language of the survey to use (default from Survey).
                Defaults to None.
            graph: Export graphs. Defaults to False.
            group_ids: Question groups to generate statistics from. Defaults to None.

        Returns:
            Bytes length written to file.
        """
        content = await self.export_statistics(
            survey_id,
            file_format=file_format,
            language=language,
            graph=graph,
            group_ids=group_ids,
        )
        return await asyncio.to_thread(Path(filename).write_bytes, content)

    async def get_uploaded_file_objects(
        self,
        survey_id: int,
        token: str | None = None,
        response_id: int | None = None,
    ) -> AsyncGenerator[types.ReadableFile, None]:
        """Iterate over uploaded files in a survey response.

        Either a token or a response ID is required.

        Args:
            survey_id: Survey for which to download files.
            token: Get the files uploaded by this response token.
            response_id: Get the files uploaded to this response.

        Yields:
            :class:`~citric.types.ReadableFile` dictionaries.
        """
        files_data = await self.get_uploaded_files(survey_id, token, response_id)
        for file in files_data:
            yield {
                "meta": files_data[file]["meta"],
                "content": io.BytesIO(base64.b64decode(files_data[file]["content"])),
            }

    async def download_files(
        self,
        directory: str | Path,
        survey_id: int,
        token: str | None = None,
        response_id: int | None = None,
    ) -> list[Path]:
        """Download files uploaded in survey response.

        Either a token or a response ID is required. The files are written in worker
        threads, so the event loop isn't blocked.

        Args:
            directory: Where to store the files.
            survey_id: Survey for which to download files.
            token: Get the files uploaded by this response token.
            response_id: Get the files uploaded to this response.

        Returns:
            List with the paths of downloaded files.
        """
        dirpath = Path(directory)

        filepaths = []
        uploaded_files = self.get_uploaded_file_objects(
            survey_id,
            token=token,
            response_id=response_id,
        )

        async for file in uploaded_files:
            filepath = dirpath / file["meta"]["filename"]
            filepaths.append(filepath)
            await asyncio.to_thread(filepath.write_bytes, file["content"].read())

        return filepaths

    async def upload_file(
        self,
        survey_id: int,
        field: str,
        path: PathLike[str],
        *,
        filename: str | None = None,
    ) -> types.FileUploadResult:
        """Upload a file to a LimeSurvey survey from a local path.

        The file is read in a worker thread, so the event loop isn't blocked.

        Args:
            survey_id: ID of the survey to which the file belongs.
            field: Field to upload the file to.
            path: Path to the file to upload.
            filename: Optional filename override to use in LimeSurvey.

        Returns:
            File metadata with final upload path.
        """
        path = Path(path)
        if filename is None:
            filename = path.name

        content = await asyncio.to_thread(path.read_bytes)
        return await self.upload_file_object(
            survey_id,
            field,
            filename,
            io.BytesIO(content),
        )
