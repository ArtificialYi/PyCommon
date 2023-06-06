import secrets


class RandomTool:
    __BITS = 63
    DOWN = (1 << __BITS) - 1

    @classmethod
    def random(cls) -> float:
        return secrets.randbits(cls.__BITS) / cls.DOWN
    pass
