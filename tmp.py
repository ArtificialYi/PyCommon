import asyncio
from src.tcp.server import server_main


if __name__ == '__main__':
    asyncio.run(server_main('192.168.0.2', 12345))
    pass
