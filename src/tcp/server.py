from asyncio import Server, StreamReader, StreamWriter
import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED

from ..exception.tcp import ConnException

from ..flow.server import FlowJsonDeal, FlowRecv, FlowSendServer


async def __handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f'Connection from {addr}')

    async with (
        FlowSendServer(writer) as flow_send,
        FlowJsonDeal(flow_send) as flow_json,
        FlowRecv(reader, flow_json) as flow_recv,
    ):
        set_task = {flow_send.task, flow_json.task, flow_recv.task}
        try:
            done, _ = await asyncio.wait(set_task, return_when=FIRST_COMPLETED)
            done.pop().result()
            pass
        except ConnException as e:
            print(f'Connection from {addr} is closing: {e}')
            pass
        except asyncio.CancelledError:
            print(f'Connection from {addr} is closing')
            raise
        except BaseException as e:
            print(f'什么异常:{type(e)}|{e}')
            raise e
        finally:
            for task in set_task:
                task.cancel()
                pass
            await asyncio.wait(set_task, return_when=ALL_COMPLETED)
            writer.close()
            await writer.wait_closed()
            print('Closed the connection')
            pass
    pass


async def start_server(host: str, port: int):
    return await asyncio.start_server(__handle_client, host, port,)


async def main(server: Server):
    async with server:
        await server.serve_forever()
        pass
    pass
