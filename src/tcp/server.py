from asyncio import StreamReader, StreamWriter
import asyncio


async def __handle_client(reader: StreamReader, writer: StreamWriter):
    addr = writer.get_extra_info('peername')
    print(f'Connection from {addr}')

    # 启动各种流
    while True:
        data = await reader.read(1)
        if not data:
            break

        message = data.decode('utf-8')
        print(f'Received {message} from {addr}')

        response = f'Server received: {message}\r\n'
        writer.write(response.encode('utf-8'))
        await writer.drain()
        pass

    print(f'Closing the connection with {addr}')
    writer.close()
    await writer.wait_closed()
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
