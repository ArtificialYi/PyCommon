import os


COMMON_CONFIG_DIR = os.path.dirname(__file__)
COMMON_SRC_ROOT = os.path.dirname(COMMON_CONFIG_DIR)
COMMON_ROOT = os.path.dirname(COMMON_SRC_ROOT)

MODULES_ROOT = os.path.dirname(COMMON_ROOT)
SRC_ROOT = os.path.dirname(MODULES_ROOT)
PROJECT_ROOT = os.path.dirname(SRC_ROOT)
CONFIG_ROOT = os.path.join(PROJECT_ROOT, 'configuration')
