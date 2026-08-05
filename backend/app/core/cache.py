from collections.abc import Awaitable
from typing import Any, Protocol


class RedisProtocol(Protocol):
    def set(self, key: str, value: str, /, ex: int | None = None) -> Awaitable[Any]: ...
    def exists(self, key: str, /) -> Awaitable[int]: ...
