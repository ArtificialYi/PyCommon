from .norm.env import get_value_by_tag_and_field


class TcpConfigManage:
    @staticmethod
    async def get_trans_bytes():
        return int(await get_value_by_tag_and_field('common_tcp', 'trans_bytes'))
    pass
