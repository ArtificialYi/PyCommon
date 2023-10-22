import asyncio
from configparser import ConfigParser
from enum import Enum
import os

from .. import CONFIG_ROOT, PROJECT_ROOT
from ...tool.map_tool import MapKeyGlobal
from .tool import ConfigTool


class EnvEnum(Enum):
    TEST = 'TEST'
    DEV = 'DEV'
    PROD = 'PROD'

    def lower(self) -> str:
        str_tmp: str = self.value
        return str_tmp.lower()
    pass


class ProjectEnv:
    @classmethod
    @MapKeyGlobal()
    async def __config_project(cls) -> ConfigParser:
        """获取项目的基础配置
        项目的基础配置 不存在 => 抛出异常
        """
        path_project_root = os.path.join(PROJECT_ROOT, 'tox.ini')
        if not os.path.exists(path_project_root):
            raise Exception(f'项目缺少必备文件:{path_project_root}')

        return await ConfigTool.get_config(path_project_root)

    @classmethod
    async def get_env(cls):
        config_project = await cls.__config_project()
        env_pre = config_project.get('hy_project', 'env_pre', fallback='HY_ENV')
        env_str = os.environ.get(env_pre, EnvEnum.DEV.value)
        return EnvEnum(env_str)

    @classmethod
    async def get_name(cls):
        config_project = await cls.__config_project()
        return config_project.get('hy_project', 'project_name', fallback='HY_PROJECT')
    pass


class ConfigEnv:
    """基础的配置读取类
    1. 排除在common自身的单测范围外
    2. 项目单测调用时需要mock
    """
    @classmethod
    @MapKeyGlobal()
    async def config_default(cls):
        """默认的项目配置文件
        """
        path_default = os.path.join(CONFIG_ROOT, 'default.ini')
        return await ConfigTool.get_config(path_default)

    @classmethod
    @MapKeyGlobal()
    async def config_env(cls):
        """环境独有的配置文件
        """
        env_project = await ProjectEnv.get_env()
        path_env = os.path.join(CONFIG_ROOT, f'{env_project.lower()}.ini')
        return await ConfigTool.get_config(path_env)
    pass


async def get_value_by_tag_and_field(tag: str, field: str):
    config_env, config_default = await asyncio.gather(ConfigEnv.config_env(), ConfigEnv.config_default())
    return ConfigTool.get_value(tag, field, config_default, config_env)
