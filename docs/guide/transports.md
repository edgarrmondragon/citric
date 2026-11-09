# HTTP Transport

Citric uses the [_adapter pattern_][adapter] to make HTTP request-handling pluggable. Under normal circumstances, you won't need anything but the default transport.

The library ships with a few transport implementations of its own:

- {class}`~citric.transport.urllib3.Urllib3Transport`
- {class}`~citric.transport.httpx2.Httpx2Transport`

but also, any object compatible with [`requests.Session`](inv:requests:py:class#requests.Session) can be used. For example:

```python
>>> import niquests  # https://niquests.readthedocs.io
>>> from citric.transport.protocol import HTTPTransport
>>> isinstance(niquests.Session(), HTTPTransport)
True
```

:::{tip}
The `HTTPTransport` class is [_runtime-checkable_](inv:python:py:function#typing.runtime_checkable).
:::

Or you can build your own by implementing the {class}`~citric.transport.protocol.HTTPTransport` protocol:

```python

```

[adapter]: https://refactoring.guru/design-patterns/adapter
