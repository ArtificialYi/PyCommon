from typing import List
from .base import DropNorm
from torch import nn
import torch


class SeqBase(DropNorm):
    """参数序列化的模型
    """
    def __init__(self, dropout: float = 0.5) -> None:
        DropNorm.__init__(self, dropout)
        self.__num_init()
        self.__prefix = ''
        pass

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, name):
        self.__prefix = name
        pass

    def __num_init(self):
        self.num_w = 0
        self.num_b = 0
        self.child_seqs: List[SeqBase] = []
        pass

    def add_seq(self, other):
        self.num_w += other.num_w
        self.num_b += other.num_b
        self.child_seqs.append(other)
        pass

    def seq_weight_init(self, seq_weight: torch.Tensor, offset: int = 0):
        """
        1. 为当前模型设置offset
        2. 为所有子模型设置offset
        """
        offset_tmp = offset
        for child in self.child_seqs:
            child.seq_weight_init(seq_weight, offset_tmp)
            offset_tmp += child.num_w
            pass
        pass

    def seq_bias_init(self, seq_bias: torch.Tensor, offset: int = 0):
        """
        1. 为当前模型设置offset
        2. 为所有子模型设置offset
        """
        offset_tmp = offset
        for child in self.child_seqs:
            child.seq_bias_init(seq_bias, offset_tmp)
            offset_tmp += child.num_b
            pass
        pass

    def get_view_iter(self):
        for child in self.child_seqs:
            for key, value in child.get_view_iter():
                yield f'{child.prefix}.{key}', value
                pass
            pass
        pass
    pass


class SeqWNLinear(SeqBase):
    def __init__(self, input_num: int, output_num: int, dropout: float = 0.5) -> None:
        SeqBase.__init__(self, dropout)
        # weight_v、weight_g、bias
        self.__input_num = input_num
        self.__output_num = output_num

        self.__num_wv = input_num * output_num
        # self.__num_wg = output_num

        # self.num_w += self.__num_wv + self.__num_wg
        self.num_w += self.__num_wv
        self.num_b += output_num
        pass

    def seq_weight_init(self, seq_weight: torch.Tensor, offset: int):
        tmp = offset + self.__num_wv
        # self.weight_v = seq_weight[offset:tmp].view(self.__input_num, self.__output_num)
        # self.weight_g = seq_weight[tmp:tmp + self.__num_wg].view(self.__output_num)
        # self.__dist = ((self.weight_v ** 2).sum() ** 0.5).item()
        self.weight = seq_weight[offset:tmp].view(self.__input_num, self.__output_num)
        pass

    def seq_bias_init(self, seq_bias: torch.Tensor, offset: int):
        self.bias = seq_bias[offset:offset + self.num_b].view(self.num_b)
        pass

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        # dist = (self.weight_v ** 2).sum() ** 0.5
        return input @ self.weight + self.bias
        # return (input @ self.weight_v) * (self.weight_g / dist) + self.bias

    def get_view_iter(self):
        yield 'weight', self.weight.T.data
        yield 'bias', self.bias.data
        pass
    pass


class SeqLinearUnit(SeqBase):
    def __init__(self, input_num: int, output_num: int, hidden_num: int, layer_scale: float = 2, dropout: float = 0.5) -> None:
        SeqBase.__init__(self, dropout)

        self.fc_in_x = SeqWNLinear(input_num, output_num, dropout)
        self.fc_in_x.prefix = 'fc_in_x'
        self.add_seq(self.fc_in_x)

        self.fc_in_h = SeqWNLinear(output_num, output_num, dropout)
        self.fc_in_h.prefix = 'fc_in_h'
        self.add_seq(self.fc_in_h)

        self.hidden_layers: List[SeqWNLinear] = []
        pre_num = output_num
        up_time = int(hidden_num / 2 + 0.5)
        for i in range(up_time):
            next_num = int(pre_num * layer_scale)
            fc = SeqWNLinear(pre_num, next_num, dropout)
            fc.prefix = f'fc_up_{i}'
            self.hidden_layers.append(fc)
            self.add_seq(fc)
            pre_num = next_num
            pass
        for i in range(hidden_num - up_time):
            next_num = int(pre_num / layer_scale)
            fc = SeqWNLinear(pre_num, next_num, dropout)
            fc.prefix = f'fc_down_{i}'
            self.hidden_layers.append(fc)
            self.add_seq(fc)
            pre_num = next_num
            pass
        self.fc_out = SeqWNLinear(pre_num, output_num, dropout)
        self.fc_out.prefix = 'fc_out'
        self.add_seq(self.fc_out)
        pass

    def forward(self, X0: torch.Tensor, X1: torch.Tensor) -> torch.Tensor:
        XT = self.fc_in_x(X0) + self.fc_in_h(X1)
        output = torch.sigmoid(self.drop(XT))
        for fc in self.hidden_layers:
            output = torch.sigmoid(self.drop(fc(output)))
            pass
        return XT + self.fc_out(output)
    pass


class SeqStateUnitTwo(SeqBase):
    def __init__(self, input_num: int, output_num: int, hidden_num: int, layer_scale: float = 2, dropout: float = 0.5) -> None:
        SeqBase.__init__(self, dropout=dropout)

        self.fc_switch = SeqLinearUnit(input_num, output_num, hidden_num, layer_scale, dropout)
        self.fc_switch.prefix = 'left'
        self.add_seq(self.fc_switch)
        self.fc_sign = SeqLinearUnit(input_num, output_num, hidden_num, layer_scale, dropout)
        self.fc_sign.prefix = 'right'
        self.add_seq(self.fc_sign)
        pass

    def forward(self, X0: torch.Tensor, X1: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.fc_switch(X0, X1)) - torch.sigmoid(self.fc_sign(X0, X1))
    pass


class SeqGRUUnit(SeqBase):
    def __init__(self, input_num: int, output_num: int, hidden_num: int, layer_scale: float = 2, dropout: float = 0.5):
        SeqBase.__init__(self, dropout=dropout)
        self.history_num = output_num

        # self.fc_xh = SeqStateUnitTwo(input_num, output_num, hidden_num, layer_scale, dropout)
        # self.add_seq(self.fc_xh)

        self.fc_r = SeqStateUnitTwo(input_num, output_num, hidden_num, layer_scale, dropout)
        self.fc_r.prefix = 'fc_r'
        self.add_seq(self.fc_r)
        self.fc_z = SeqLinearUnit(input_num, output_num, hidden_num, layer_scale, dropout)
        self.fc_z.prefix = 'fc_z'
        self.add_seq(self.fc_z)

        self.fc_ht = SeqStateUnitTwo(input_num, output_num, hidden_num, layer_scale, dropout)
        self.fc_ht.prefix = 'fc_ht'
        self.add_seq(self.fc_ht)
        pass

    def forward(self, X: torch.Tensor, history: torch.Tensor) -> torch.Tensor:
        if history is None:
            history = torch.zeros(self.history_num).type_as(X)
            pass
        # XH = self.fc_xh(X, history)
        h_r = self.fc_r(X, history) * history
        h_t = self.fc_ht(X, h_r)
        z = torch.sigmoid(self.fc_z(X, history))
        return z * h_t + (1 - z) * history
    pass


class SeqModule(SeqBase):
    """
    1. 无法变更数据类型
    2. storage有可能发生变更
    """
    def __init__(
        self, input_num: int, output_num: int, hidden_num: int, layer_scale: float = 1.5,
        dropout: float = 0.5, dtype: torch.dtype = torch.double,
    ) -> None:
        super().__init__(dropout)
        self.seq_gru = SeqGRUUnit(input_num, output_num, hidden_num, layer_scale, dropout)
        self.add_seq(self.seq_gru)

        self.weight = nn.Parameter(torch.zeros(1, self.seq_gru.num_w, dtype=dtype))
        nn.init.kaiming_normal_(self.weight)

        self.bias = nn.Parameter(torch.zeros(self.seq_gru.num_b, dtype=dtype))
        # nn.init.normal_(self.bias)

        # 将数据同步至子模型
        self.__weight_init()
        pass

    def __weight_init(self):
        self.seq_weight_init(self.weight[0])
        self.seq_bias_init(self.bias)
        pass

    # def bias_init(self):
    #     self.bias = nn.Parameter(torch.zeros(self.seq_gru.num_b, dtype=self.bias.dtype))
    #     self.__weight_init()
    #     pass

    def forward(self, X: torch.Tensor, history: torch.Tensor):
        return self.seq_gru(X, history)
    pass
