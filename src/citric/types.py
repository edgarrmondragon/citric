"""Citric Python types (deprecated module, use citric._types)."""  # noqa: A005, I002

import typing as t


def __getattr__(name: str) -> t.Any:  # noqa: ANN401 # pragma: no cover
    import warnings  # noqa: PLC0415

    warnings.warn(
        "citric.types is deprecated, use citric._types instead",
        DeprecationWarning,
        stacklevel=2,
    )

    from . import _types  # noqa: PLC0415

    return getattr(_types, name)
