from asyncio import FIRST_COMPLETED, StreamReader, StreamWriter
import asyncio
from contextlib import asynccontextmanager

from ..exception.tcp import ConnException
from ..tool.base import AsyncBase
from ..flow.server import FlowJsonDeal, FlowRecv, FlowSendServer


async def __handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f'Connection from {addr}')

    async with (
        FlowSendServer(writer) as flow_send,
        FlowJsonDeal(flow_send) as flow_json,
        FlowRecv(reader, flow_json) as flow_recv,
    ):
        done, _ = await asyncio.wait([flow_send, flow_json, flow_recv], return_when=FIRST_COMPLETED)
        pass
    try:
        done.pop().result()
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
