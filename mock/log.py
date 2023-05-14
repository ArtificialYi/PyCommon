from aiologger import Logger

from ..src.tool.map_tool import MapKey


@MapKey()
async def get_mock_logger():
    print('testtestestsetsetsteste')
    return Logger.with_default_handlers()
