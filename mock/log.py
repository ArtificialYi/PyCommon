from aiologger import Logger

from ..src.tool.map_tool import MapKey


@MapKey()
async def get_mock_logger():
    return Logger.with_default_handlers()
