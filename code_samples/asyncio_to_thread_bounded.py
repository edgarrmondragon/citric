# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Bound the concurrency of ``asyncio.to_thread`` calls to match the connection pool."""

# ruff: file-ignore[print]

# start example
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from citric import Client
from citric.transport.urllib3 import Urllib3Transport

if TYPE_CHECKING:
    from citric.types import QuestionsListElement

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"
MAX_CONCURRENCY = 8


async def main() -> None:
    """Fetch the questions of all surveys with bounded concurrency."""
    # Size the connection pool to the number of concurrent requests, otherwise
    # connections above `maxsize` are discarded after use instead of being reused.
    transport = Urllib3Transport(maxsize=MAX_CONCURRENCY)

    # `to_thread` uses the loop's default executor, which can grow to
    # `min(32, cpu_count + 4)` threads. A semaphore keeps the load on the
    # LimeSurvey server predictable regardless of that number.
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    client = Client(LS_URL, "iamadmin", "secret", transport=transport)

    try:

        async def questions_for(sid: int) -> list[QuestionsListElement]:
            async with semaphore:
                return await asyncio.to_thread(client.list_questions, sid)

        surveys = await asyncio.to_thread(client.list_surveys)

        # If a call fails, the task group cancels the others and raises an
        # `ExceptionGroup`. Cancelling a task doesn't stop its thread though, so
        # calls already running may still be in flight when the client is closed.
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(questions_for(s["sid"])) for s in surveys]

        for survey, task in zip(surveys, tasks, strict=True):
            print(survey["sid"], len(task.result()), "questions")

    finally:
        # `close` sends a blocking request to release the session key, so keep it
        # off the event loop.
        # Shielding it lets the request finish even if this task is cancelled.
        await asyncio.shield(asyncio.to_thread(client.close))


asyncio.run(main())
# end example
