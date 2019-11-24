"""Tests for JSON-RPC."""
import uuid

import pytest

from limette.rpc import Session, RPCResponse, BaseRPC, JSONRPC
from limette.exceptions import (LimeSurveyStatusError,
                                LimeSurveyError,
                                LimeSurveyApiError)


MOCK_URL = 'http://example.com'
MOCK_USERNAME = 'limeuser'
MOCK_PASSWORD = 'limesecret'


class MockJSONRPC(BaseRPC):

    valid_url = MOCK_URL
    username = MOCK_USERNAME
    password = MOCK_PASSWORD

    def __init__(self):
        self.valid_keys = set()

    @staticmethod
    def _generate_key():
        return uuid.uuid4()

    def invoke(self, url, method, *args, request_id=1):

        if method == 'not_valid':
            response = RPCResponse(result=None, error='Some Error', id=1)
            self.raise_for_response(response)

        if method == 'get_session_key':
            username, password = args
            if username == self.username and password == self.password:
                key = self._generate_key()
                self.valid_keys.add(key)
                response = RPCResponse(key, None, request_id)
            else:
                response = RPCResponse(
                    {'status': 'Invalid user name or password'},
                    None,
                    request_id
                )

            self.raise_for_response(response)
            return response

        elif method == 'release_session_key':
            key = args[0]
            if key in self.valid_keys:
                self.valid_keys.remove(key)

        else:
            key, *params = args
            if key in self.valid_keys:
                response = RPCResponse(
                    {'key': key, 'params': params},
                    None,
                    request_id,
                )
            else:
                response = RPCResponse(
                    {'status': 'Invalid session key'},
                    None,
                    request_id
                )

            self.raise_for_response(response)
            return response


@pytest.fixture
def session():
    url = MOCK_URL
    username = MOCK_USERNAME
    password = MOCK_PASSWORD
    spec = MockJSONRPC()

    session = Session(url, username, password, spec)

    yield session

    session.close()


def test_json_rpc(requests_mock):

    spec = JSONRPC()

    requests_mock.post(MOCK_URL, text='{"error":null,"result":"OK","id":1}')
    response = spec.invoke(MOCK_URL, 'some_method')

    assert response.result == 'OK'
    assert response.error is None
    assert response.id == 1


@pytest.mark.parametrize('message', [None, 'Test message'])
def test_status_exception(message):
    default = LimeSurveyError.default

    with pytest.raises(LimeSurveyError) as excinfo:
        raise LimeSurveyError(message)

    exc = excinfo.value
    assert str(exc) == message if message is not None else default


def test_bad_spec():
    with pytest.raises(NotImplementedError):
        class BadRPC(BaseRPC):
            pass

        bad_spec = BadRPC()
        bad_spec.invoke()


def test_session_context():
    url = MOCK_URL
    username = MOCK_USERNAME
    password = MOCK_PASSWORD
    spec = MockJSONRPC()

    with Session(url, username, password, spec) as session:
        assert len(session.spec.valid_keys) == 1

    assert len(session.spec.valid_keys) == 0


def test_api_error():
    url = MOCK_URL
    username = MOCK_USERNAME
    password = MOCK_PASSWORD
    spec = MockJSONRPC()

    with pytest.raises(LimeSurveyApiError) as excinfo:
        with Session(url, username, password, spec) as session:
            session.rpc('not_valid')

    exc = excinfo.value
    assert exc.response.result is None
    assert exc.response.error == 'Some Error'


def test_bad_credentials():
    url = MOCK_URL
    username = MOCK_USERNAME + '_bad'
    password = MOCK_PASSWORD
    spec = MockJSONRPC()

    with pytest.raises(LimeSurveyStatusError) as excinfo:
        Session(url, username, password, spec)

    exc = excinfo.value
    assert exc.response.result == {'status': 'Invalid user name or password'}
    assert exc.response.error is None


def test_rpc_valid_key(session):
    response = session.rpc('hey', 1, 2, request_id=10)
    assert response.result == {'key': session.key, 'params': [1, 2]}
    assert response.error is None
    assert response.id == 10


def test_rpc_invalid_key(session):

    session.spec.valid_keys = []

    with pytest.raises(LimeSurveyStatusError) as excinfo:
        session.rpc('hey', 1, 2, request_id=10)

    exc = excinfo.value
    assert exc.response.result == {'status': 'Invalid session key'}
    assert exc.response.error is None
    assert exc.response.id == 10
