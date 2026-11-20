# Copyright (c) 2026 Edgar Ramírez-Mondragón

# TODO(edgarrmondragon): Remove these ignore comments once the type is fixed upstream
# https://github.com/requests-cache/requests-cache/pull/1206
# mypy: disable-error-code="arg-type"
# pyright: reportArgumentType=none

"""Example of using a custom requests.Session object with the client."""

from __future__ import annotations

# start example
import requests_cache
from citric import Client

cached_session = requests_cache.CachedSession(
    expire_after=60,
    allowable_methods=["POST"],
)

client = Client(
    "https://example.com/index.php/admin/remotecontrol",
    "iamadmin",
    "secret",
    transport=cached_session,
)

# Get all surveys from user "iamadmin".
# All responses will be cached for 1 minute.
surveys = client.list_surveys("iamadmin")
# end example
