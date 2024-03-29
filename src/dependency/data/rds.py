from attr import dataclass, ib


@dataclass
class RDSConfigData:
    host: str
    port: int = ib(converter=int)
    user: str
    password: str = ib(repr=False)
    db: str
    max_conn: int = ib(converter=int)

    def to_key(self):
        return ':'.join(str(v) for v in vars(self).values())
    pass
