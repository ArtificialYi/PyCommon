from asyncio import StreamReader, StreamWriter
import asyncio
from contextlib import asynccontextmanager

from ..exception.tcp import ConnException

from ..tool.base import AsyncBase

from ..tool.func_tool import QueueException
from ..flow.server import FlowJsonDeal, FlowRecv, FlowSendServer


async def __handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f'Connection from {addr}')

    try:
        err_queue = QueueException()
        async with (
            FlowSendServer(writer, err_queue) as flow_send,
            FlowJsonDeal(flow_send, err_queue) as flow_json,
            FlowRecv(reader, flow_json, err_queue),
        ):
            await err_queue.exception_loop(3)
    except ConnException as e:
        print(f'Connection from {addr} is closing: {e}')
        pass
    finally:
        print('Closed the connection')
        writer.close()
        await writer.wait_closed()
        pass
    pass


# 服务端主流程
@asynccontextmanager
async def server_main(host: str, port: int):
    server = await asyncio.start_server(__handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        task = AsyncBase.coro2task_exec(server.serve_forever())
        await asyncio.sleep(1)
        yield task
        pass
    await asyncio.sleep(1)
    pass
