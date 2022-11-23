import zlib
import numpy as np
import torch


class BytesTool:
    @staticmethod
    def torch2bytes(data: torch.Tensor) -> bytes:
        return zlib.compress(data.numpy().tobytes(), 9)

    @staticmethod
    def bytes2torch(data: bytes) -> torch.Tensor:
        return torch.from_numpy(np.frombuffer(zlib.decompress(data)).copy())
    pass
