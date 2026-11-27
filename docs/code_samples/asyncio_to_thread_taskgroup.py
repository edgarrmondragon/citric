# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Call the blocking client concurrently with ``asyncio.TaskGroup``."""

# ruff: file-ignore[print]

from __future__ import annotations

# start example
import asyncio

from citric import Client
from citric.transport.urllib3 import Urllib3Transport

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"


async def main() -> None:
    """Fetch the language properties of all surveys concurrently."""
    # Worker threads share the transport, so use one that supports concurrent use
    transport = Urllib3Transport(maxsize=8)

    client = Client(LS_URL, "iamadmin", "secret", transport=transport)

    try:
        surveys = await asyncio.to_thread(client.list_surveys)

        # If one task fails, the group cancels the others and raises an
        # `ExceptionGroup`. Cancelling a task doesn't stop its thread, though, so
        # calls already running may still be in flight when the client is closed.
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(
                    asyncio.to_thread(client.get_language_properties, s["sid"]),
                )
                for s in surveys
            ]

        for survey, task in zip(surveys, tasks, strict=True):
            print(survey["sid"], task.result()["surveyls_title"])

    finally:
        # `close` sends a blocking request to release the session key, so keep it
        # off the event loop. Shielding it lets the request finish even if this task
        # is cancelled, but it doesn't wait for the other worker threads: calls from
        # cancelled tasks may still be running when the session key is released.
        await asyncio.shield(asyncio.to_thread(client.close))


asyncio.run(main())
# end example
