import zlib
import numpy as np
import torch


class BytesTool:
    @staticmethod
    def torch2bytes(data_tensor: torch.Tensor) -> bytes:
        data_np = data_tensor.numpy()
        data_bytes = data_np.tobytes()
        return zlib.compress(data_bytes, 9)

    @staticmethod
    def bytes2torch(data_bytes_comp: bytes) -> torch.Tensor:
        data_bytes = zlib.decompress(data_bytes_comp)
        data_np = np.frombuffer(data_bytes).copy()
        return torch.from_numpy(data_np)
    pass
