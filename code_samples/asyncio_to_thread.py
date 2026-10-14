# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""Call the blocking client concurrently with ``asyncio.to_thread``."""

# ruff: file-ignore[print]

from __future__ import annotations

# start example
import asyncio

from citric import Client

LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"


async def main() -> None:
    """Fetch the language properties of all surveys concurrently."""
    with Client(LS_URL, "iamadmin", "secret") as client:
        # One blocking call to list the surveys...
        surveys = await asyncio.to_thread(client.list_surveys, "iamadmin")

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
            print(survey["sid"], props["surveyls_welcometext"])


asyncio.run(main())
# end example
