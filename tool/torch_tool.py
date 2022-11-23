import torch


class TorchTool:
    @staticmethod
    def all_lt10(data: torch.Tensor):
        return data is None or (
            not torch.isinf(data).any() and not torch.isnan(data).any() and data.abs().max().item() < 10
        )
    pass
