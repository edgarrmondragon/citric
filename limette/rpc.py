"""Low level wrapper for connecting to the LSRC2."""
from collections import namedtuple

import requests

from limette.exceptions import LimeSurveyStatusError, LimeSurveyApiError


RPCResponse = namedtuple('RPCResponse', 'result error id')


class BaseRPC:
    def invoke(self):
        raise NotImplementedError

    @staticmethod
    def raise_for_response(response: RPCResponse):
        """"""
        if isinstance(response.result, dict):
            status = response.result.get('status')
            if status is not None:
                raise LimeSurveyStatusError(response)
        elif response.error is not None:
            raise LimeSurveyApiError(response)


class JSONRPC(BaseRPC):
    _headers = {
        'content-type': 'application/json',
        'user-agent': 'jsonrpc-client',
    }

    def __init__(self):
        self.request_session = requests.Session()
        self.request_session.headers.update(self._headers)

    def invoke(self, url, method, *args, request_id=1):

        payload = {
            'method': method,
            'params': [*args],
            'id': request_id,
        }

        res = self.request_session.post(url, json=payload)
        response = RPCResponse(**res.json())

        self.raise_for_response(response)

        return response


class Session(object):
    """LimeSurvey RemoteControl 2 API session.

    :param url: LimeSurvey Remote Control endpoint.
    :type url: ``str``
    :param admin_user: LimeSurvey user name.
    :type admin_user: ``str``
    :param admin_pass: LimeSurvey password.
    :type admin_pass: ``str``
    :param spec: RPC specification
    :type spec: ``BaseRPC``
    """

    __attrs__ = ['url', 'key']

    def __init__(self, url, admin_user, admin_pass, spec=JSONRPC()):
        """Create LimeSurvey wrapper."""
        self.url = url
        self.spec = spec
        self.key = self.get_session_key(admin_user, admin_pass)

    def rpc(self, method, *args, request_id=1):
        r"""Authenticated call to an RPC method on LimeSurvey.

        :param method: Name of the method to call.
        :type method: ``str``
        :param \*args: Postional arguments of the RPC method.
        :type \*args: ``Any``
        :param request_id: Request ID for response validation.
        :type request_id: ``int``
        """
        return self.spec.invoke(self.url,
                                method,
                                self.key,
                                *args,
                                request_id=request_id,
                                )

    def get_session_key(self, admin_user, admin_pass, request_id=1):
        """Get RC API session key."""
        response = self.spec.invoke(self.url,
                                    'get_session_key',
                                    admin_user,
                                    admin_pass,
                                    request_id=request_id,
                                    )

        if response.error is None:
            return response.result

    def close(self):
        """Close RC API session."""
        self.rpc('release_session_key')

    def __enter__(self):
        """Context manager for API session."""
        return self

    def __exit__(self, type, value, traceback):
        """Safely exit an API session."""
        self.close()
