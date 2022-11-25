from ...src.tool.torch_tool import TorchTool
import torch
import numpy as np
from torch import nn


class TestTorchTool:
    def test(self):
        data_torch0 = torch.zeros(5).double().requires_grad_(False)
        nn.init.uniform_(data_torch0)
        # None也通过
        assert TorchTool.all_lt10(None)
        assert TorchTool.all_lt10(data_torch0)

        # 存在一个inf就不通过
        data_torch0[0] = np.inf
        assert torch.isinf(data_torch0[0])
        assert not TorchTool.all_lt10(data_torch0)
        data_torch0[0] = -np.Inf
        assert torch.isinf(data_torch0[0])
        assert not TorchTool.all_lt10(data_torch0)

        # 存在一个nan也通不过
        data_torch0[0] = np.nan
        assert torch.isnan(data_torch0[0])
        assert not TorchTool.all_lt10(data_torch0)
        data_torch0[0] = -np.NaN
        assert torch.isnan(data_torch0[0])
        assert not TorchTool.all_lt10(data_torch0)

        # 存在一个大于10的数也通不过
        data_torch0[0] = 10.1
        assert not TorchTool.all_lt10(data_torch0)

        # 设置回来就通过了
        data_torch0[0] = 10
        assert TorchTool.all_lt10(data_torch0)
        pass
    pass
