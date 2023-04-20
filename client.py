import asyncio

import aioconsole

from src.tool.base import AsyncBase
from src.tcp.client import TcpApiManage


async def main():
    host = '127.0.0.1'
    port = 12345
    while True:
        data = await aioconsole.ainput('input:')
        AsyncBase.coro2task_exec(TcpApiManage.service(host, port, data))
        pass
    pass


if __name__ == '__main__':
    asyncio.run(main())
    pass
