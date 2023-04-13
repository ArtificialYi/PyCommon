from configparser import ConfigParser
from enum import Enum
import os

from ..src.tool.map_tool import MapKey


from .tool import ConfigTool


COMMON_CONFIGURATION_DIR = os.path.dirname(__file__)
COMMON_ROOT = os.path.dirname(COMMON_CONFIGURATION_DIR)
PROJECT_ROOT = os.path.dirname(COMMON_ROOT)


class EnvEnum(Enum):
    TEST = 'TEST'
    DEV = 'DEV'
    PRE = 'PRE'

    def lower(self) -> str:
        str_tmp: str = self.value
        return str_tmp.lower()
    pass


class ConfigEnv:
    """基础的配置读取类
    1. 排除在common自身的单测范围外
    2. 项目单测调用时需要mock
    """
    @classmethod
    @MapKey()
    async def __config_project(cls) -> ConfigParser:
        """获取项目的基础配置
        项目的基础配置 不存在 => 抛出异常
        """
        path_project_root = os.path.join(PROJECT_ROOT, 'tox.ini')
        if not os.path.exists(path_project_root):
            raise Exception(f'项目缺少必备文件:{path_project_root}')

        return await ConfigTool.get_config(path_project_root)

    @classmethod
    async def __env_enum_project(cls) -> EnvEnum:
        """获取项目环境
        """
        config_project = await cls.__config_project()
        env_pre = config_project.get('hy_project', 'env_pre', fallback='HY_ENV')
        env_str = os.environ.get(env_pre, EnvEnum.DEV.value)
        return EnvEnum(env_str)

    @classmethod
    async def __path_resource_root(cls) -> str:
        """项目配置器根目录
        """
        config_project = await cls.__config_project()
        return os.path.join(
            '/usr/local/resource',
            config_project.get('hy_project', 'name', fallback='hy_project')
        )

    @classmethod
    @MapKey()
    async def config_default(cls):
        """默认的项目配置文件
        """
        path_default = os.path.join(await cls.__path_resource_root(), 'default.ini')
        return await ConfigTool.get_config(path_default)

    @classmethod
    @MapKey()
    async def config_env(cls):
        """环境独有的配置文件
        """
        dir_root = await cls.__path_resource_root()
        env_project = await cls.__env_enum_project()
        path_env = os.path.join(dir_root, f'{env_project.lower()}.ini')
        return await ConfigTool.get_config(path_env)
    pass
