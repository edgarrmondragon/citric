# HTTP Transports

By default, {class}`Client <citric.Client>` and
{class}`Session <citric.session.Session>` send requests with a
{py:class}`requests.Session`. Under
normal circumstances, you won't need anything but the default transport.

To make HTTP request-handling pluggable, citric uses the
[_adapter pattern_][adapter]. Any object that implements the
{class}`HTTPTransport <citric.transport.protocol.HTTPTransport>` protocol can be
passed as `transport` instead.

The default is a {py:class}`requests.Session`, which honors the proxy
environment variables (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`), `.netrc`
credentials and `REQUESTS_CA_BUNDLE`. Any subclass, or object compatible with
it, is also a valid transport. For example, you can use
[`requests-cache`](inv:requests-cache:std#general) to cache the requests and
reduce the load on your server in read-intensive applications:

```{literalinclude} ../code_samples/custom_requests_session.py
:start-after: start example
:end-before: end example
```

The library also ships with a few transport implementations of its own:

- {class}`citric.transport.urllib3.Urllib3Transport`, backed by
  [`urllib3`](https://urllib3.readthedocs.io) directly, without `requests` in
  the loop. `urllib3` is a dependency of citric, so you don't need to install
  anything else. It doesn't read the proxy environment variables.

- {class}`citric.transport.httpx2.Httpx2Transport`, backed by
  [`httpx2`](https://github.com/pydantic/httpx2). It isn't a dependency of
  citric itself, so install it separately with `pip install httpx2`.

Or you can build your own by implementing the {class}`~citric.transport.protocol.HTTPTransport` protocol:

```{literalinclude} ../code_samples/custom_transport.py
:start-after: start example
:end-before: end example
```

:::{tip}
The `HTTPTransport` class is [_runtime-checkable_](inv:python:py:function#typing.runtime_checkable).
:::

[adapter]: https://refactoring.guru/design-patterns/adapter
