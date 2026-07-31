# Copyright (c) 2026 Edgar Ramírez-Mondragón

"""A client to the LimeSurvey Remote Control API 2, written in modern Python."""

__lazy_modules__ = {
    "citric.client",
    "citric.rest",
}

from citric import objects
from citric.client import Client, ServerVersion
from citric.rest import RESTClient

__version__: str = "2.3.0"

__all__ = ["Client", "RESTClient", "ServerVersion", "objects"]
