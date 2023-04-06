from asyncio import StreamReader, StreamWriter
import asyncio

from ..flow.base import FlowRecv

from ..flow.server import FlowJsonDealForServer, FlowSendServer


async def __server_flow(reader: StreamReader, writer: StreamWriter):
    async with (
        FlowSendServer(writer) as flow_send,
        FlowJsonDealForServer(flow_send) as flow_json,
        FlowRecv(reader, flow_json),
    ):
        while True:
            # 无限循环，直到连接断开。
            # TODO: 时间间隔修正
            await asyncio.sleep(1)
            pass


async def __handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f'Connection from {addr}')

    try:
        await __server_flow(reader, writer)
    except Exception as e:
        print(f'Connection from {addr} is closed: {e}')
        pass
    print('Close the connection')
    pass


# 服务端主流程
async def server_main(host: str, port: int):
    server = await asyncio.start_server(__handle_client, host, port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()
        pass
    pass
