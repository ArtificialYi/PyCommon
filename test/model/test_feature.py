from ...src.model.feature import SeqModule
import torch


class TestSeqModule:
    def test(self):
        """创建新模型
        1. 创建模型，尝试对一个输出计算
        2. 创建新模型，试着覆盖旧模型，对相同的输出进行重复计算，观察结果是否一致（期望是不一致）
        """
        input_num = 63
        output_num = 32
        hidden_num = 2
        scale = 1.5
        # 基本模型
        m0 = SeqModule(input_num, output_num, hidden_num, scale).eval()
        input_data = torch.ones(input_num).double()
        assert not m0.seq_gru.fc_ht.fc_sign.fc_out.training
        history_out0 = m0(input_data, None)
        history_out1 = m0(input_data, None)
        assert torch.abs(history_out0 - history_out1).sum() < 1e-4
        assert not m0.seq_gru.fc_ht.fc_sign.fc_out.training

        # 模型更新
        m0.load_state_dict(SeqModule(input_num, output_num, hidden_num, scale).state_dict())
        history_out2 = m0(input_data, None)
        assert not m0.seq_gru.fc_ht.fc_sign.fc_out.training
        assert torch.abs(history_out0 - history_out2).sum() > 1e-4
        history_out3 = m0(input_data, history_out2)
        assert torch.abs(history_out2 - history_out3).sum() > 1e-4

        # 模型训练模式开关
        m0.train()
        assert m0.seq_gru.fc_ht.fc_sign.fc_out.training

        m0.eval()
        assert not m0.seq_gru.fc_ht.fc_sign.fc_out.training

        # 子模型名称是否均在
        assert len(list(m0.get_view_iter())) == (hidden_num + 3) * 10
        pass
    pass
