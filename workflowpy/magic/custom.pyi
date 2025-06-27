from typing import Any, LiteralString, overload

from .types import _ValueType

@overload
def action(
    id: LiteralString, params: dict[LiteralString, Any], output: None = None
) -> None: ...
@overload
def action(
    id: LiteralString, params: dict[LiteralString, Any], output: tuple[str, _ValueType]
) -> None: ...
def attachment(value: Any) -> Any: ...
def string(*values: Any) -> Any: ...
