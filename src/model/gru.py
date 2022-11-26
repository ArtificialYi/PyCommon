from typing import List, Tuple
from torch import nn
import torch


class MultiLinear(nn.Module):
    """多项式特征扩充
    """
    def __init__(self, num_input: int, num_output: int, err: float = 1e-6):
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


class SigmoidUnit(nn.Module):
    def __init__(self, input_num: int, output_num: int, hidden_num: int):
        nn.Module.__init__(self)
        self.fc_in_x = MultiLinear(input_num, output_num)
        self.ln_in_x = nn.LayerNorm(output_num)

        self.fc_in_h = MultiLinear(output_num, output_num)
        self.ln_in_h = nn.LayerNorm(output_num)

        self.__hidden_layers: List[Tuple[MultiLinear, nn.LayerNorm]] = []
        for i in range(hidden_num):
            fc = MultiLinear(output_num, output_num)
            ln = nn.LayerNorm(output_num)
            self.__hidden_layers.append((fc, ln))
            self.add_module(f'fc_{i}', fc)
            self.add_module(f'ln_{i}', ln)
            pass

        self.fc_out = MultiLinear(output_num, output_num)
        self.ln_out = nn.LayerNorm(output_num)
        pass

    def forward(self, X0: torch.Tensor, X1: torch.Tensor):
        residual = self.ln_in_x(self.fc_in_x(X0)) + self.ln_in_h(self.fc_in_h(X1))
        output = torch.sigmoid(residual)
        for fc, ln in self.__hidden_layers:
            residual = residual + ln(fc(output))
            output = torch.sigmoid(residual)
            pass
        return torch.sigmoid(residual + self.ln_out(self.fc_out(output)))
    pass


class CrossUnit(nn.Module):
    def __init__(self, input_num: int, output_num: int, hidden_num: int):
        nn.Module.__init__(self)
        self.left = SigmoidUnit(input_num, output_num, hidden_num)
        self.right = SigmoidUnit(input_num, output_num, hidden_num)
        pass

    def forward(self, X0: torch.Tensor, X1: torch.Tensor):
        return self.left(X0, X1) - self.right(X0, X1)
    pass


class GRUUnit(nn.Module):
    def __init__(self, input_num: int, output_num: int, hidden_num: int):
        nn.Module.__init__(self)
        self.__history_num = output_num

        self.fc_r = CrossUnit(input_num, output_num, hidden_num)
        self.fc_ht = CrossUnit(input_num, output_num, hidden_num)
        self.fc_z = SigmoidUnit(input_num, output_num, hidden_num)
        self.eval()
        pass

    def forward(self, X: torch.Tensor, history: torch.Tensor):
        history = torch.zeros(self.__history_num).type_as(X) if history is None else history
        h_r = self.fc_r(X, history) * history
        h_t = self.fc_ht(X, h_r)
        z = self.fc_z(X, history)
        return z * h_t + (1 - z) * history
    pass
