import os

from configparser import ConfigParser

from .tool import ConfigTool

from .. import COMMON_CONFIG_DIR, COMMON_ROOT, CONFIG_ROOT, PROJECT_ROOT

from ...tool.env_tool import EnvEnum


class ProjectEnv:
    @classmethod
    def __config_project(cls) -> ConfigParser:
        """获取项目的基础配置
        项目的基础配置 不存在 => 抛出异常
        """
        path_base = os.path.join(PROJECT_ROOT, 'tox.ini')
        if not os.path.exists(path_base):
            # raise Exception(f'项目缺少必备文件:{path_project_root}')
            path_base = os.path.join(COMMON_ROOT, 'tox.ini')
            pass

        return ConfigTool.get_config(path_base)

    @classmethod
    def get_env(cls):
        config_project = cls.__config_project()
        env_pre = config_project.get('hy_project', 'env_pre', fallback='HY_ENV')
        env_str = os.environ.get(env_pre, EnvEnum.DEV.value)
        return EnvEnum(env_str)

    @classmethod
    def get_name(cls):
        config_project = cls.__config_project()
        return config_project.get('hy_project', 'project_name', fallback='HY_PROJECT')
    pass


class ConfigEnv:
    """基础的配置读取类
    1. 排除在common自身的单测范围外
    2. 项目单测调用时需要mock
    """
    @classmethod
    def config_default(cls):
        """默认的项目配置文件
        """
        path_default = os.path.join(CONFIG_ROOT, 'default.ini')
        return ConfigTool.get_config(path_default)

    @classmethod
    def config_env(cls):
        """环境独有的配置文件
        """
        env_project = ProjectEnv.get_env()
        path_env = os.path.join(CONFIG_ROOT, f'{env_project.lower()}.ini')
        return ConfigTool.get_config(path_env)

    @classmethod
    def config_common(cls):
        path_common = os.path.join(COMMON_CONFIG_DIR, 'default.ini')
        return ConfigTool.get_config(path_common)
    pass


def get_value_by_tag_and_field(tag: str, field: str):
    config_env, config_default = ConfigEnv.config_env(), ConfigEnv.config_default()
    config_common = ConfigEnv.config_common()
    return ConfigTool.get_value(tag, field, config_common, config_default, config_env)
