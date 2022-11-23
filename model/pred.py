import torch
from torch import nn


class PyramidOut(nn.Module):
    """
    基本元件: 映射至输出层时使用
    """
    def __init__(self, input_num: int, output_num: int, hidden_num: int):
        super().__init__()
        self.fc_in = nn.Linear(input_num, input_num)
        nn.init.xavier_normal_(self.fc_in.weight)
        self.ln_in = nn.LayerNorm(input_num)

        self.hidden_layers = []
        for idx in range(hidden_num):
            fc = nn.Linear(input_num, input_num)
            ln = nn.LayerNorm(input_num)
            self.hidden_layers.append((fc, ln))
            nn.init.xavier_normal_(fc.weight)
            self.add_module(f'fc_{idx}', fc)
            self.add_module(f'ln_{idx}', ln)
            pass

        self.fc_x = nn.Linear(input_num, output_num)
        nn.init.xavier_normal_(self.fc_x.weight)
        self.ln_x = nn.LayerNorm(output_num)

        self.fc_out = nn.Linear(input_num, output_num)
        nn.init.xavier_normal_(self.fc_out.weight)
        self.ln_out = nn.LayerNorm(output_num)

        self.__lr_dict = {
            'fc_out.weight': 1,
            'fc_out.bias': 1,
            'fc_0.weight': 1,
            'fc_0.bias': 1,
            'fc_in.weight': 1,
            'fc_in.bias': 1,
            'fc_x.weight': 1,
            'fc_x.bias': 1,
        }
        pass

    def forward(self, X: torch.Tensor):
        residual = self.ln_in(self.fc_in(X))
        output = torch.sigmoid(residual)
        for fc, ln in self.hidden_layers:
            residual = residual + ln(fc(output))
            output = torch.sigmoid(residual)
            pass
        return self.ln_x(self.fc_x(residual)) + self.ln_out(self.fc_out(output))

    def get_lr_dict(self):  # pragma: no cover
        return self.__lr_dict
    pass


if __name__ == '__main__':
    pass
