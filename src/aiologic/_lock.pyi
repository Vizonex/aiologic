#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Ilya Egorov <0x42005e1f@gmail.com>
# SPDX-License-Identifier: ISC

import sys

from types import TracebackType
from typing import Any

from .lowlevel import Event

if sys.version_info >= (3, 13):
    from warnings import deprecated
else:
    from typing_extensions import deprecated

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

class PLock:
    __slots__ = (
        "__weakref__",
        "_impl",
    )

    @deprecated("Use BinarySemaphore instead")
    def __new__(cls, /) -> Self: ...
    def __init_subclass__(cls, /, **kwargs: Any) -> None: ...
    def __getstate__(self, /) -> None: ...
    def __repr__(self, /) -> str: ...
    def __bool__(self, /) -> bool: ...
    async def __aenter__(self, /) -> Self: ...
    def __enter__(self, /) -> Self: ...
    async def __aexit__(
        self,
        /,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
    def __exit__(
        self,
        /,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
    async def _async_acquire(self, /, *, blocking: bool = True) -> bool: ...
    async def async_acquire(self, /, *, blocking: bool = True) -> bool: ...
    def _green_acquire(
        self,
        /,
        *,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> bool: ...
    def green_acquire(
        self,
        /,
        *,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> bool: ...
    def _release(self, /) -> None: ...
    def async_release(self, /) -> None: ...
    def green_release(self, /) -> None: ...
    def locked(self, /) -> bool: ...
    @property
    def waiting(self, /) -> int: ...

    # Internal methods used by condition variables

    def _park(self, /, token: list[Any]) -> bool: ...
    def _unpark(self, /, event: Event) -> None: ...
    def _after_park(self, /) -> None: ...

class BLock(PLock):
    __slots__ = ()

    @deprecated("Use BoundedBinarySemaphore instead")
    def __new__(cls, /) -> Self: ...
    def __init_subclass__(cls, /, **kwargs: Any) -> None: ...

class Lock(PLock):
    __slots__ = (
        # "__weakref__",
        "_owner",
        "_releasing",
        "_unlocked",
        "_waiters",
    )

    def __new__(cls, /) -> Self: ...
    def __getstate__(self, /) -> None: ...
    def __repr__(self, /) -> str: ...
    def __bool__(self, /) -> bool: ...
    async def __aenter__(self, /) -> Self: ...
    def __enter__(self, /) -> Self: ...
    async def __aexit__(
        self,
        /,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
    def __exit__(
        self,
        /,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
    def _acquire_nowait(self, /) -> bool: ...
    async def _async_acquire_on_behalf_of(
        self,
        /,
        task: tuple[str, int],
        count: int = 1,
        *,
        blocking: bool = True,
        _shield: bool = False,
    ) -> bool: ...
    def _green_acquire_on_behalf_of(
        self,
        /,
        task: tuple[str, int],
        count: int = 1,
        *,
        blocking: bool = True,
        timeout: float | None = None,
        _shield: bool = False,
    ) -> bool: ...
    async def async_acquire(self, /, *, blocking: bool = True) -> bool: ...
    def green_acquire(
        self,
        /,
        *,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> bool: ...
    def _release(self, /) -> None: ...
    def async_release(self, /) -> None: ...
    def green_release(self, /) -> None: ...
    def async_owned(self, /) -> bool: ...
    def green_owned(self, /) -> bool: ...
    def locked(self, /) -> bool: ...
    @property
    def owner(self, /) -> tuple[str, int] | None: ...
    @property
    def waiting(self, /) -> int: ...

    # Internal methods used by condition variables

    def _park(self, /, token: list[Any]) -> bool: ...
    def _unpark(
        self,
        /,
        event: Event,
        state: tuple[tuple[str, int], int] | None = None,
    ) -> None: ...
    def _after_park(self, /) -> None: ...

class RLock(Lock):
    __slots__ = ("_count",)

    def __new__(cls, /) -> Self: ...
    async def _async_acquire_on_behalf_of(
        self,
        /,
        task: tuple[str, int],
        count: int = 1,
        *,
        blocking: bool = True,
        _shield: bool = False,
    ) -> bool: ...
    def _green_acquire_on_behalf_of(
        self,
        /,
        task: tuple[str, int],
        count: int = 1,
        *,
        blocking: bool = True,
        timeout: float | None = None,
        _shield: bool = False,
    ) -> bool: ...
    async def async_acquire(
        self,
        /,
        count: int = 1,
        *,
        blocking: bool = True,
    ) -> bool: ...
    def green_acquire(
        self,
        /,
        count: int = 1,
        *,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> bool: ...
    def _release(self, /) -> None: ...
    def async_release(self, /, count: int = 1) -> None: ...
    def green_release(self, /, count: int = 1) -> None: ...
    @property
    def count(self, /) -> int: ...
    @property
    @deprecated("Use 'count' instead")
    def level(self, /) -> int: ...
