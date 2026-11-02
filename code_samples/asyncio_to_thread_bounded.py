# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Bound the concurrency of ``asyncio.to_thread`` calls to match the connection pool."""

# ruff: file-ignore[print]

# start example
import asyncio

from citric import Client
from citric.transport.urllib3 import Urllib3Transport
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

        # Cancelling a task doesn't stop its thread, so gather every result, even
        # failed ones, to wait for all the threads before the client is closed.
        results = await asyncio.gather(
            *(questions_for(s["sid"]) for s in surveys),
            return_exceptions=True,
        )

        for survey, result in zip(surveys, results, strict=True):
            if isinstance(result, BaseException):
                raise result
            print(survey["sid"], len(result), "questions")

    finally:
        # `close` sends a blocking request to release the session key, so keep it
        # off the event loop.
        # Shielding it lets the request finish even if this task is cancelled.
        await asyncio.shield(asyncio.to_thread(client.close))


asyncio.run(main())
# end example
