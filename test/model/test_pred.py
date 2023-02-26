import torch
from ...src.model.pred import PyramidOut


class TestPyramidOut:
    def test(self):
        """
        校验pred模型的层数
        pred模型跑通
        """
        history_num = 64
        hidden_num = 2
        output_num = 5
        m_pred = PyramidOut(history_num, output_num, hidden_num).double().eval()
        assert len(list(m_pred.named_parameters())) == (hidden_num + 3) * 10
        assert not m_pred.training

        data_history = torch.randn(history_num).double()
        data_output0 = m_pred.forward(data_history)
        data_output1 = m_pred(data_history)
        assert torch.allclose(data_output0, data_output1)
        pass
    pass
