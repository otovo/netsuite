import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Type, Union
from uuid import UUID

__all__ = ("dumps", "loads")

try:
    import orjson as _json
except ImportError:
    import json as _json  # type: ignore[no-redef]

    HAS_ORJSON = False
else:
    HAS_ORJSON = True


loads = _json.loads


def dumps(obj: Any, *args, **kw) -> str:
    if not HAS_ORJSON:
        return _json.dumps(obj, *args, **kw)  # type: ignore[return-value]
    kw["default"] = _orjson_default
    return _json.dumps(obj, *args, **kw).decode("utf-8")


def _orjson_default(obj: Any) -> Any:
    """Handle cases which orjson doesn't know what to do with"""

    if isinstance(obj, str):
        return str(obj)
    encoder = _get_encoder(obj)
    return encoder(obj)


def _isoformat(o: Union[datetime.date, datetime.time]) -> str:
    return o.isoformat()


def _get_encoder(obj: Any) -> Any:
    for base in obj.__class__.__mro__[:-1]:
        try:
            encoder = _ENCODERS_BY_TYPE[base]
        except KeyError:
            continue
        return encoder(obj)
    raise TypeError(
        f"Object of type '{obj.__class__.__name__}' is not JSON serializable"
    )


_ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    bytes: lambda o: o.decode(),
    datetime.date: _isoformat,
    datetime.datetime: _isoformat,
    datetime.time: _isoformat,
    datetime.timedelta: lambda td: td.total_seconds(),
    Decimal: float,
    Enum: lambda o: o.value,
    frozenset: list,
    Path: str,
    set: list,
    UUID: str,
}
