import asyncio
from src.tcp.server import server_main


if __name__ == '__main__':
    asyncio.run(server_main('0.0.0.0', 12345))
    pass
