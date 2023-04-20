from src.tcp.client import TcpApi, TcpApiManage


async def service(host: str, port: int, path: str, *args, **kwds):
    tcp: TcpApi = TcpApiManage.get_tcp(host, port)
    return await tcp.api(path, *args, **kwds)
