import asyncio
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

from .func_tool import ExceptTool

from ..exception.tcp import ServiceExistException, ServiceNotFoundException


C = TypeVar('C', bound=Callable)


class ServerRegister:
    __TABLE: Dict[str, Tuple[Callable, bool]] = dict()

    def __init__(self, path: Optional[str] = None):
        self.__path = path
        pass

    def __call__(self, func: C) -> C:
        path = f'{"" if self.__path is None else self.__path}/{func.__name__}'
        if path in self.__class__.__TABLE:  # pragma: no cover
            raise ServiceExistException(f'服务已存在，无法注册:{path}')
        self.__class__.__TABLE[path] = func, asyncio.iscoroutinefunction(func)
        return func

    @classmethod
    async def __call_unit(cls, path, *args, **kwds) -> Tuple[Callable, bool]:
        if path not in cls.__TABLE:
            raise ServiceNotFoundException(f'服务不存在:{path}')
        func, is_async = cls.__TABLE[path]
        func_res = func(*args, **kwds)
        return await func_res if is_async else func_res

    @classmethod
    async def call(cls, path, *args, **kwds) -> Any:
        try:
            return await cls.__call_unit(path, *args, **kwds)
        except BaseException as e:
            print(f'服务:{path}|{args}|{kwds}|遇到|{type(e).__name__}|{e}')
            ExceptTool.raise_not_exception(e)
            return e
    pass
