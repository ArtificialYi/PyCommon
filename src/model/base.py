from torch import nn
import torch


class DropNorm(nn.Module):
    """带dropout的模型
    """
    def __init__(self, dropout: float = 0.5) -> None:
        super().__init__()
        self.drop = nn.Dropout(dropout)
        pass
    pass


class MultiLinear(nn.Module):
    """多项式特征扩充
    """
    def __init__(self, num_input: int, num_output: int, err: float = 5e-5):
        super().__init__()
        self.__err = err

        self.fc_in = nn.Linear(num_input, num_output)
        nn.init.xavier_normal_(self.fc_in.weight)
        self.ln_in = nn.LayerNorm(num_output)

        self.fc_out_multi = nn.Linear(num_output, num_output)
        nn.init.xavier_normal_(self.fc_out_multi.weight)
        self.fc_out_in = nn.Linear(num_input, num_output)
        nn.init.xavier_normal_(self.fc_out_in.weight)
        pass

    def forward(self, X: torch.Tensor):
        X_abs = torch.log(torch.abs(X) + self.__err)
        X_multi = torch.exp(self.ln_in(self.fc_in(X_abs)))
        return self.fc_out_in(X) + self.fc_out_multi(X_multi)
    pass
