# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Bound the concurrency of ``asyncio.to_thread`` calls to match the connection pool."""

# ruff: file-ignore[print]

from __future__ import annotations

# start example
import asyncio

from citric import Client
from requests import Session
from requests.adapters import HTTPAdapter

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"
MAX_CONCURRENCY = 8


async def main() -> None:
    """Fetch the questions of all surveys with bounded concurrency."""
    # Size the connection pool to the number of concurrent requests, otherwise
    # `requests` discards connections above its default of 10.
    transport = Session()
    adapter = HTTPAdapter(pool_connections=1, pool_maxsize=MAX_CONCURRENCY)
    transport.mount("https://", adapter)
    transport.mount("http://", adapter)

    # `to_thread` uses the loop's default executor, which can grow to
    # `min(32, cpu_count + 4)` threads. A semaphore keeps the load on the
    # LimeSurvey server predictable regardless of that number.
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    with Client(LS_URL, "iamadmin", "secret", transport=transport) as client:

        async def questions_for(sid: int) -> list[dict]:
            async with semaphore:
                return await asyncio.to_thread(client.list_questions, sid)

        surveys = await asyncio.to_thread(client.list_surveys, "iamadmin")

        # TaskGroup cancels the remaining tasks if any request fails
        async with asyncio.TaskGroup() as tg:
            tasks = {s["sid"]: tg.create_task(questions_for(s["sid"])) for s in surveys}

        for sid, task in tasks.items():
            print(sid, len(task.result()), "questions")


asyncio.run(main())
# end example
