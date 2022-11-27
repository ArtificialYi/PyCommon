from ...src.model.pred import PyramidOut
from ...src.model.feature import SeqModule
import torch


class TestPyramidOut:
    def test(self):
        """
        校验pred模型的层数
        pred模型跑通
        """
        input_num = 5
        history_num = 64
        hidden_num = 2
        output_num = 5
        scale = 1.5
        m_feature = SeqModule(input_num, history_num, hidden_num, scale).eval()
        m_pred = PyramidOut(history_num, output_num, hidden_num).double().eval()
        assert len(list(m_pred.named_parameters())) == (hidden_num + 3) * 10

        input_data = torch.ones(input_num).double()
        history_data = m_feature(input_data, None)
        output_data = torch.softmax(m_pred(history_data), dim=0)
        assert output_data.shape[0] == output_num
        assert torch.argmax(output_data).item() < 5
        assert abs(output_data.sum() - 1) < 1e-4
        assert not m_feature.training
        assert not m_pred.training
        pass
    pass
