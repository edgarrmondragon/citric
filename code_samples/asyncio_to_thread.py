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
        properties = await asyncio.gather(
            *(
                asyncio.to_thread(client.get_language_properties, s["sid"])
                for s in surveys
            )
        )

        for survey, props in zip(surveys, properties, strict=True):
            print(survey["sid"], props["surveyls_title"])


asyncio.run(main())
# end example
