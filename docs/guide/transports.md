# HTTP Transports

By default, {class}`Client <citric.Client>` and
{class}`Session <citric.session.Session>` send requests with `urllib3`. Under
normal circumstances, you won't need anything but the default transport.

To make HTTP request-handling pluggable, citric uses the
[_adapter pattern_][adapter]. Any object that implements the
{class}`HTTPTransport <citric.transport.protocol.HTTPTransport>` protocol (a
`request` method and a `close` method) can be passed as `transport`
instead.

The library ships with a few transport implementations of its own:

- {class}`citric.transport.urllib3.Urllib3Transport` (the default), backed by
  [`urllib3`](https://urllib3.readthedocs.io) directly, without `requests` in
  the loop. `urllib3` is a dependency of citric, so it is installed with it and
  you don't need to install anything else.

- {class}`citric.transport.httpx2.Httpx2Transport`, backed by
  [`httpx2`](https://github.com/pydantic/httpx2). It isn't a dependency of
  citric itself, so install it separately with `pip install httpx2`.

Any subclass of, or object compatible with, the
[`requests.Session`](inv:requests:py:class#requests.Session) class is
also a valid transport. `requests` is not a dependency of citric, so install it
separately (`pip install requests`) if you use it. For example, you can use
[`requests-cache`](inv:requests-cache:std#general) to cache the requests and
reduce the load on your server in read-intensive applications:

```{literalinclude} ../code_samples/custom_requests_session.py
:start-after: start example
:end-before: end example
```

Or you can build your own by implementing the {class}`~citric.transport.protocol.HTTPTransport` protocol:

```python

```

:::{tip}
The `HTTPTransport` class is [_runtime-checkable_](inv:python:py:function#typing.runtime_checkable).
:::

[adapter]: https://refactoring.guru/design-patterns/adapter
