from asyncio import StreamReader, StreamWriter
import asyncio

from ..flow.client import FlowJsonDealForServer, FlowRecv, FlowSendServer


async def __server_flow(reader: StreamReader, writer: StreamWriter):
    async with (
        FlowSendServer(writer) as flow_send,
        FlowJsonDealForServer(flow_send) as flow_json,
        FlowRecv(reader, flow_json),
    ):
        while True:
            await asyncio.sleep(1)
            pass


async def __handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f'Connection from {addr}')

    # 无限调用接收流，直到连接断开
    try:
        await __server_flow(reader, writer)
    except Exception as e:
        print(f'Connection from {addr} is closed: {e}')
        pass
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
