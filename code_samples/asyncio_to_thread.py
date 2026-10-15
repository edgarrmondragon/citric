# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Call the blocking client concurrently with ``asyncio.to_thread``."""

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

    with Client(LS_URL, "iamadmin", "secret", transport=transport) as client:
        # One blocking call to list the surveys...
        surveys = await asyncio.to_thread(client.list_surveys)

        # ...then one blocking call per survey, all running in worker threads.
        # `Session` authenticates lazily and thread-safely, so concurrent calls
        # on a fresh client share a single session key.
        # `return_exceptions=True` makes `gather` wait for every worker thread, even
        # if some calls fail. Cancelling a task doesn't stop its thread, and the
        # client must not be closed while requests are still in flight.
        results = await asyncio.gather(
            *(
                asyncio.to_thread(client.get_language_properties, s["sid"])
                for s in surveys
            ),
            return_exceptions=True,
        )

        for survey, result in zip(surveys, results, strict=True):
            if isinstance(result, BaseException):
                raise result
            print(survey["sid"], result["surveyls_title"])


asyncio.run(main())
# end example
