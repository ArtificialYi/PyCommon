from ...src.tool.bytes_tool import BytesTool
import torch
from torch import nn


class TestBytesTool:
    def test(self):
        """torch转换后数据不变
        1. 生成一个随机torch
        2. torch2bytes
        3. bytes2torch
        4. 与原数据做比较
        """
        data_tensor_0 = torch.zeros(5).double().requires_grad_(False)
        nn.init.uniform_(data_tensor_0)

        # detach+clone可以复制一个全新的torch
        data_tensor_1 = data_tensor_0.detach().clone()
        nn.init.uniform_(data_tensor_1)
        assert (data_tensor_0 - data_tensor_1).abs().sum() > 1e-4

        # 证明转换没有对原数据造成影响
        data_tensor_2 = data_tensor_0.detach().clone()
        data_bytes = BytesTool.torch2bytes(data_tensor_2)
        data_tensor_3 = BytesTool.bytes2torch(data_bytes)
        assert (data_tensor_0 - data_tensor_2).abs().sum() < 1e-4
        assert (data_tensor_0 - data_tensor_3).abs().sum() < 1e-4
        pass
    pass
