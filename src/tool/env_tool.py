from enum import Enum


class EnvEnum(Enum):
    TEST = 'TEST'
    DEV = 'DEV'
    PRE = 'PRE'
    PROD = 'PROD'

    def lower(self) -> str:
        str_tmp: str = self.value
        return str_tmp.lower()
    pass
