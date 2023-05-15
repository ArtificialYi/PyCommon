import pytest
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
        data_tensor0 = torch.zeros(5).double().requires_grad_(False)
        nn.init.uniform_(data_tensor0)

        # detach+clone可以复制一个全新的torch
        data_tensor1 = data_tensor0.detach().clone()
        nn.init.uniform_(data_tensor1)
        assert (data_tensor0 - data_tensor1).abs().sum() > 1e-4

        # 证明转换没有对原数据造成影响（数据类型必须为double）
        data_tensor2 = data_tensor0.detach().clone()
        data_bytes0 = BytesTool.torch2bytes(data_tensor2)
        data_tensor3 = BytesTool.bytes2torch(data_bytes0)
        assert (data_tensor0 - data_tensor2).abs().sum() < 1e-4
        assert (data_tensor0 - data_tensor3).abs().sum() < 1e-4

        # float类型会报错
        data_tensor4 = torch.zeros(5).float().requires_grad_(False)
        nn.init.uniform_(data_tensor4)
        data_bytes1 = BytesTool.torch2bytes(data_tensor4)
        with pytest.raises(ValueError):
            BytesTool.bytes2torch(data_bytes1)
        pass
    pass
