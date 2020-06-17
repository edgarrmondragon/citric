"""XML-RPC implementation."""
from citric.rpc.base import BaseRPC


class XMLRPC(BaseRPC):
    """Execute XML-RPC in LimeSurvey."""

    _headers = {
        "content-type": "application/xml",
        "user-agent": "citric-client",
    }

    def __init__(self) -> None:  # noqa: ANN101
        """Create an XML-RPC interface."""
        super().__init__()
