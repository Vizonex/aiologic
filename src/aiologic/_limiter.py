#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Ilya Egorov <0x42005e1f@gmail.com>
# SPDX-License-Identifier: ISC

from __future__ import annotations

from types import MappingProxyType, TracebackType
from typing import TYPE_CHECKING, Any

from ._semaphore import BinarySemaphore, Semaphore
from .lowlevel import (
    async_checkpoint,
    current_async_task_ident,
    current_green_task_ident,
    green_checkpoint,
)

if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self


class CapacityLimiter:
    __slots__ = (
        "__weakref__",
        "_borrowers",
        "_borrowers_proxy",
        "_semaphore",
    )

    def __new__(cls, /, total_tokens: int | None = None) -> Self:
        if total_tokens is None:
            total_tokens = 1
        elif total_tokens < 0:
            msg = "total_tokens must be >= 0"
            raise ValueError(msg)

        self = object.__new__(cls)

        self._borrowers = {}
        self._borrowers_proxy = MappingProxyType(self._borrowers)

        if total_tokens >= 2:
            self._semaphore = Semaphore(total_tokens)
        else:
            self._semaphore = BinarySemaphore(total_tokens)

        return self

    def __getnewargs__(self, /) -> tuple[Any, ...]:
        if (total_tokens := self._semaphore.initial_value) != 1:
            return (total_tokens,)

        return ()

    def __getstate__(self, /) -> None:
        return None

    def __repr__(self, /) -> str:
        cls = self.__class__
        cls_repr = f"{cls.__module__}.{cls.__qualname__}"

        object_repr = f"{cls_repr}({self._semaphore.initial_value!r})"

        available_tokens = self._semaphore.value

        if available_tokens > 0:
            extra = f"available_tokens={available_tokens}"
        else:
            waiting = self._semaphore.waiting

            extra = f"available_tokens={available_tokens}, waiting={waiting}"

        return f"<{object_repr} at {id(self):#x} [{extra}]>"

    def __bool__(self, /) -> bool:
        return self._semaphore.initial_value > self._semaphore.value

    async def __aenter__(self, /) -> Self:
        await self.async_acquire()

        return self

    def __enter__(self, /) -> Self:
        self.green_acquire()

        return self

    async def __aexit__(
        self,
        /,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.async_release()

    def __exit__(
        self,
        /,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.green_release()

    async def async_acquire(self, /, *, blocking: bool = True) -> bool:
        task = current_async_task_ident()

        if task in self._borrowers:
            msg = (
                "the current task is already holding"
                " one of this capacity limiter's tokens",
            )
            raise RuntimeError(msg)

        success = await self._semaphore.async_acquire(blocking=blocking)

        if success:
            self._borrowers[task] = 1

        return success

    def green_acquire(
        self,
        /,
        *,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> bool:
        task = current_green_task_ident()

        if task in self._borrowers:
            msg = (
                "the current task is already holding"
                " one of this capacity limiter's tokens",
            )
            raise RuntimeError(msg)

        success = self._semaphore.green_acquire(
            blocking=blocking,
            timeout=timeout,
        )

        if success:
            self._borrowers[task] = 1

        return success

    def async_release(self, /) -> None:
        task = current_async_task_ident()

        try:
            del self._borrowers[task]
        except KeyError:
            msg = (
                "the current task is not holding"
                " any of this capacity limiter's tokens"
            )
            raise RuntimeError(msg) from None

        self._semaphore.async_release()

    def green_release(self, /) -> None:
        task = current_green_task_ident()

        try:
            del self._borrowers[task]
        except KeyError:
            msg = (
                "the current task is not holding"
                " any of this capacity limiter's tokens"
            )
            raise RuntimeError(msg) from None

        self._semaphore.green_release()

    def async_borrowed(self, /) -> bool:
        return current_async_task_ident() in self._borrowers

    def green_borrowed(self, /) -> bool:
        return current_green_task_ident() in self._borrowers

    @property
    def total_tokens(self, /) -> int:
        return self._semaphore.initial_value

    @property
    def available_tokens(self, /) -> int:
        return self._semaphore.value

    @property
    def borrowed_tokens(self, /) -> int:
        return self._semaphore.initial_value - self._semaphore.value

    @property
    def borrowers(self, /) -> MappingProxyType[tuple[str, int], int]:
        return self._borrowers_proxy

    @property
    def waiting(self, /) -> int:
        return self._semaphore.waiting


class RCapacityLimiter(CapacityLimiter):
    __slots__ = ()

    async def async_acquire(
        self,
        /,
        count: int = 1,
        *,
        blocking: bool = True,
    ) -> bool:
        if count < 1:
            msg = "count must be >= 1"
            raise ValueError(msg)

        task = current_async_task_ident()

        try:
            current_count = self._borrowers[task]
        except KeyError:
            pass
        else:
            if blocking:
                await async_checkpoint()

            self._borrowers[task] = current_count + count

            return True

        success = await self._semaphore.async_acquire(blocking=blocking)

        if success:
            self._borrowers[task] = count

        return success

    def green_acquire(
        self,
        /,
        count: int = 1,
        *,
        blocking: bool = True,
        timeout: float | None = None,
    ) -> bool:
        if count < 1:
            msg = "count must be >= 1"
            raise ValueError(msg)

        task = current_green_task_ident()

        try:
            current_count = self._borrowers[task]
        except KeyError:
            pass
        else:
            if blocking:
                green_checkpoint()

            self._borrowers[task] = current_count + count

            return True

        success = self._semaphore.green_acquire(
            blocking=blocking,
            timeout=timeout,
        )

        if success:
            self._borrowers[task] = count

        return success

    def async_release(self, /, count: int = 1) -> None:
        if count < 1:
            msg = "count must be >= 1"
            raise ValueError(msg)

        task = current_async_task_ident()

        try:
            current_count = self._borrowers[task]
        except KeyError:
            msg = (
                "the current task is not holding"
                " any of this capacity limiter's tokens"
            )
            raise RuntimeError(msg) from None

        if current_count > count:
            self._borrowers[task] = current_count - count
        elif current_count == count:
            del self._borrowers[task]

            self._semaphore.async_release()
        else:
            msg = "capacity limiter released too many times"
            raise RuntimeError(msg)

    def green_release(self, /, count: int = 1) -> None:
        if count < 1:
            msg = "count must be >= 1"
            raise ValueError(msg)

        task = current_green_task_ident()

        try:
            current_count = self._borrowers[task]
        except KeyError:
            msg = (
                "the current task is not holding"
                " any of this capacity limiter's tokens"
            )
            raise RuntimeError(msg) from None

        if current_count > count:
            self._borrowers[task] = current_count - count
        elif current_count == count:
            del self._borrowers[task]

            self._semaphore.green_release()
        else:
            msg = "capacity limiter released too many times"
            raise RuntimeError(msg)

    def async_count(self, /) -> int:
        return self._borrowers.get(current_async_task_ident(), 0)

    def green_count(self, /) -> int:
        return self._borrowers.get(current_green_task_ident(), 0)
