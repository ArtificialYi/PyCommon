import asyncio
from typing import Any, Callable, Dict, Optional, Tuple

from .func_tool import ExceptTool

from ...configuration.log import LoggerLocal
from ..exception.tcp import ServiceExistException, ServiceNotFoundException


class ServerRegister:
    __TABLE: Dict[str, Tuple[Callable, bool]] = dict()

    def __init__(self, path: Optional[str] = None):
        self.__path = path
        pass

    def __call__(self, func: Callable):
        path = f'{ "" if self.__path is None else self.__path}/{func.__name__}'
        if self.__class__.__TABLE.get(path) is not None:  # pragma: no cover
            raise ServiceExistException(f'服务已存在，无法注册:{path}')
        self.__class__.__TABLE[path] = func, asyncio.iscoroutinefunction(func)
        return func

    @classmethod
    async def __call_unit(cls, path, *args, **kwds) -> Tuple[Callable, bool]:
        if cls.__TABLE.get(path) is None:
            raise ServiceNotFoundException(f'服务不存在:{path}')
        func, is_async = cls.__TABLE[path]
        func_res = func(*args, **kwds)
        return await func_res if is_async else func_res

    @classmethod
    async def call(cls, path, *args, **kwds) -> Any:
        try:
            return await cls.__call_unit(path, *args, **kwds)
        except BaseException as e:
            await LoggerLocal.exception(e, f'服务:{path}|{args}|{kwds}|遇到|{type(e).__name__}|{e}')
            ExceptTool.raise_not_exception(e)
            return e
    pass