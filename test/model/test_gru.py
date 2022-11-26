from ...src.model.gru import GRUUnit
import torch


class TestGRUUnit:
    def test_parameters(self):
        """构建一个GRUUnit
        1. 创建一个模型
        2. 查看模型的参数是否一致
        3. 非训练模式下的相同参数预测，结果应一致
        4. 训练模式下的相同参数训练，结果应一致（没有dropout)
        """
        input_num = 63
        hidden_num = 2
        output_num = 64

        m0 = GRUUnit(input_num, output_num, hidden_num).double()
        named_parameters = list(m0.named_parameters())
        assert len(named_parameters) == (hidden_num + 3) * 50

        assert not m0.training
        input_data = torch.ones(input_num).double()
        history_out0 = m0(input_data, None)
        history_out1 = m0(input_data, None)
        assert torch.abs(history_out0 - history_out1).sum() < 1e-4

        m0.train()
        assert m0.training
        history_out2 = m0(input_data, None)
        history_out3 = m0(input_data, None)
        assert torch.abs(history_out2 - history_out3).sum() < 1e-4

        m0.eval()
        assert not m0.training
        pass
    pass
