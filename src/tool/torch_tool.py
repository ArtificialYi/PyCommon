from typing import Union
import torch


class TorchTool:
    @staticmethod
    def all_lt10(data: Union[torch.Tensor, None]):
        return data is None or not (
            torch.isinf(data).any() or torch.isnan(data).any() or data.abs().max().item() > 10
        )
    pass
