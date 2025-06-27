from typing import Any, Literal, LiteralString, overload

def shortcut_input() -> Any: ...
@overload
def fetch(
    url: str,
    *,
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
    headers: dict[str, str] = ...,
) -> File: ...
@overload
def fetch(
    url: str,
    *,
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
    headers: dict[str, str] = ...,
    data: Any,
) -> File: ...
@overload
def fetch(
    url: str,
    *,
    method: Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] = 'GET',
    headers: dict[str, str] = ...,
    json: Any,
) -> File: ...

class App:
    @property
    def is_running(self) -> bool: ...

class File:
    @property
    def file_size(self) -> FileSize: ...

class FileSize(
    _Measurement[Literal['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']]
): ...

class _Measurement[U: LiteralString]:
    def __lt__(self, other: tuple[float, U]) -> bool: ...
    def __gt__(self, other: tuple[float, U]) -> bool: ...
    def __le__(self, other: tuple[float, U]) -> bool: ...
    def __ge__(self, other: tuple[float, U]) -> bool: ...
    def __eq__(self, other: tuple[float, U]) -> bool: ...
    def __ne__(self, other: tuple[float, U]) -> bool: ...
