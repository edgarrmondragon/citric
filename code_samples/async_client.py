# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Fetch the questions of all surveys concurrently with the async client."""

# ruff: file-ignore[print]

from __future__ import annotations

# start example
import asyncio

from citric.aio import AsyncClient
from citric.aio.transport.httpx2 import AsyncHttpx2Transport

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"


async def main() -> None:
    """Fetch the questions of all surveys of a user."""
    # Requests above `max_connections` wait for a free connection, so this also
    # bounds the load on the LimeSurvey server
    transport = AsyncHttpx2Transport(max_connections=8)

    async with AsyncClient(LS_URL, "iamadmin", "secret", transport=transport) as client:
        surveys = await client.list_surveys("iamadmin")

        # Concurrent tasks sharing a new client authenticate only once. If a call
        # fails, the other tasks are cancelled and an `ExceptionGroup` is raised.
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(client.list_questions(s["sid"])) for s in surveys]

        for survey, task in zip(surveys, tasks, strict=True):
            print(survey["surveyls_title"], len(task.result()), "questions")


asyncio.run(main())
# end example
