import asyncio
import aioconsole
from src.tcp.client import TcpApi, TcpApiManage
from src.tool.base import AsyncBase


async def main():
    tcp: TcpApi = TcpApiManage.get_tcp('127.0.0.1', 12345)
    while True:
        input_data = await aioconsole.ainput('input: ')
        if input_data == 'exit':
            break
        AsyncBase.coro2task_exec(tcp.api(input_data))
        pass
    pass


if __name__ == '__main__':
    asyncio.run(main())
    pass
