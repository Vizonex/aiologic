#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2025 Ilya Egorov <0x42005e1f@gmail.com>
# SPDX-License-Identifier: ISC

import sys

from abc import ABC, abstractmethod
from typing import Any, TypeVar, overload

from ._executors import TaskExecutor
from ._results import Result

if sys.version_info >= (3, 11):
    from typing import TypeVarTuple, Unpack
else:
    from typing_extensions import TypeVarTuple, Unpack

if sys.version_info >= (3, 9):
    from collections.abc import Callable, Coroutine, Generator
else:
    from typing import Callable, Coroutine, Generator

_T = TypeVar("_T")
_Ts = TypeVarTuple("_Ts")

class Task(Result[_T], ABC):
    __slots__ = (
        "_args",
        "_cancelled",
        "_executor",
        "_func",
        "_started",
    )

    @overload
    def __init__(
        self,
        func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
        /,
        *args: Unpack[_Ts],
        executor: TaskExecutor,
    ) -> None: ...
    @overload
    def __init__(
        self,
        func: Callable[[Unpack[_Ts]], _T],
        /,
        *args: Unpack[_Ts],
        executor: TaskExecutor,
    ) -> None: ...
    def __repr__(self, /) -> str: ...
    def __await__(self) -> Generator[Any, Any, _T]: ...
    def wait(self, timeout: float | None = None) -> _T: ...
    def cancel(self, /) -> Result[bool]: ...
    def cancelled(self, /) -> Result[bool]: ...
    def running(self, /) -> Result[bool]: ...
    def done(self, /) -> Result[bool]: ...
    @abstractmethod
    def _run(self, /) -> Coroutine[Any, Any, _T] | _T: ...
    @abstractmethod
    def _cancel(self, /) -> Coroutine[Any, Any, bool] | bool: ...
    @property
    def executor(self, /) -> TaskExecutor: ...

def _get_threading_task_class() -> type[Task[_T]]: ...
def _get_eventlet_task_class() -> type[Task[_T]]: ...
def _get_gevent_task_class() -> type[Task[_T]]: ...
def _get_asyncio_task_class() -> type[Task[_T]]: ...
def _get_curio_task_class() -> type[Task[_T]]: ...
def _get_trio_task_class() -> type[Task[_T]]: ...
def _get_anyio_task_class() -> type[Task[_T]]: ...
@overload
def _create_threading_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_threading_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_eventlet_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_eventlet_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_gevent_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_gevent_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_asyncio_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_asyncio_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_curio_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_curio_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_trio_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_trio_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_anyio_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def _create_anyio_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor,
) -> Task[_T]: ...
@overload
def create_task(
    func: Callable[[Unpack[_Ts]], Coroutine[Any, Any, _T]],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor | None = None,
) -> Task[_T]: ...
@overload
def create_task(
    func: Callable[[Unpack[_Ts]], _T],
    /,
    *args: Unpack[_Ts],
    executor: TaskExecutor | None = None,
) -> Task[_T]: ...
