from configparser import ConfigParser
from enum import Enum
import os
from ..tool.base import ConfigBase

COMMON_REPOSITORY_DIR = os.path.dirname(__file__)
COMMON_SRC_DIR = os.path.dirname(COMMON_REPOSITORY_DIR)
COMMON_ROOT = os.path.dirname(COMMON_SRC_DIR)
PROJECT_ROOT = os.path.dirname(COMMON_ROOT)

PROJECT_INI = os.path.join(PROJECT_ROOT, 'config_base.ini')
PROJECT_INI = PROJECT_INI if os.path.exists(PROJECT_INI) else os.path.join(COMMON_ROOT, 'config_base.ini')


class EnvEnum(Enum):
    TEST = 'TEST'
    DEV = 'DEV'
    PRE = 'PRE'

    def lower(self) -> str:
        str_tmp: str = self.value
        return str_tmp.lower()
    pass


class ConfigEnv:
    __PROJECT = None
    __DEFAULT = None
    __ENV = None

    @classmethod
    def __config_project(cls) -> ConfigParser:
        if cls.__PROJECT is not None:
            return cls.__PROJECT

        cls.__PROJECT = ConfigBase.get_config(PROJECT_INI)
        return cls.__PROJECT

    @classmethod
    def __path_resource(cls) -> str:
        return os.path.join(
            '/usr/local/resource',
            cls.__config_project().get('project', 'name', fallback='default')
        )

    @classmethod
    def config_default(cls):
        if cls.__DEFAULT is not None:
            return cls.__DEFAULT

        path_default = os.path.join(cls.__path_resource(), 'default.ini')
        cls.__DEFAULT = ConfigBase.get_config(path_default)
        return cls.__DEFAULT

    @classmethod
    def __env_enum(cls) -> EnvEnum:
        env_pre = cls.__config_project().get('project', 'env_pre', fallback='default')
        env_str = os.environ.get(env_pre, EnvEnum.DEV.value)
        return EnvEnum(env_str)

    @classmethod
    def config_env(cls):
        if cls.__ENV is not None:
            return cls.__ENV

        path_env = os.path.join(cls.__path_resource(), f'{cls.__env_enum().lower()}.ini')
        cls.__ENV = ConfigBase.get_config(path_env)
        return cls.__ENV
    pass
