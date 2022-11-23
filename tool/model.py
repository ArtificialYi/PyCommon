import math
import torch


class FeatureGenerator:
    """特征生成器
    1. 可以插入新数据
    2. 可以判断特征是否已生成（可以是内部函数）
    3. 可以获取特征（如果尚未生成，则返回None）
    """
    def __init__(self, time: int, feature: torch.Tensor) -> None:
        self.__time_head = None
        self.__time_tail = time
        self.__feature_head = None
        self.__feature_head_trans = None
        self.__feature_tail = feature.detach().clone()
        self.__feature_tail_trans = FeatureGenerator.__feature2trans(feature)
        self.__time_delta = torch.zeros(1).type_as(self.__feature_tail)
        self.__feature = None
        pass

    @property
    def feature(self):
        return self.__feature

    # @staticmethod
    # def __feature2trans_old(feature: torch.Tensor):
    #     trans = feature.detach_().clone()
    #     trans[1:9][trans[1:9] < 1e-9] = 1
    #     trans[10:21][trans[10:21] < 1e-9] = 1

    #     trans[1:7] = (trans[1:7] - 1) * 10
    #     trans[7:9] = (trans[7:9] - 1) * 100
    #     trans[10] = (trans[10] - 1) * 20
    #     trans[11:21] = (trans[11:21] - 1) * 10
    #     trans[21:] = trans[21:] * 500
    #     return trans

    # @staticmethod
    # def __feature2delta_old(tail: torch.Tensor, head: torch.Tensor):
    #     feature_delta = tail - head
    #     feature_delta[1:3] *= 10
    #     feature_delta[3] *= 10
    #     feature_delta[10] *= 2
    #     feature_delta[11:21] *= 20
    #     return feature_delta

    @staticmethod
    def __feature2trans(feature: torch.Tensor):
        """特征转换
        1. 0：日期差取log：0-6
        2. 1-4：价位相关比例：0.95-1.05，有时候会是0
        3. 5-6：固定比例：0.95，1.05
        4. 7-8：价位相关比例：0.95-1.05
        5. 9：成交量比持仓量取log：log2((0-N)+1)=0-X，对成交量差敏感
        6. 10：今持仓比昨持仓取log：(0-N]
        7. 11-20：价位相关比例：0.96-1.05,有可能为0
        8. 21-30：待成交量比例：0-N(基本都集中在0.001以内) 对小数敏感
        """
        trans = feature.detach().clone()

        trans[0] /= 10
        trans[1:9][trans[1:9] < 1e-6] = 1
        trans[1:9] = torch.log2(trans[1:9]) * 10  # 有正有负
        trans[9] = math.log2(max(1e-6, trans[9].item())) / 10  # 一个处于-2-10之间的值
        trans[10] = torch.log2(trans[10])  # 有正有负
        trans[11:21][trans[11:21] < 1e-6] = 1
        trans[11:21] = torch.log2(trans[11:21]) * 10  # 有正有负
        trans[21:][trans[21:] < 1e-6] = 1e-6
        trans[21:] = torch.log2(trans[21:]) / 10  # 处于-2-0之间的值
        return trans

    @staticmethod
    def __feature2delta(delta_trans: torch.Tensor, delta_origin: torch.Tensor, data_tail: torch.Tensor):
        """特征变动
        1. 0: 日期差: 绝大部分时候为0，变更时为大于0的很小数
        2. 1-4: 价位变更: 绝大部分时候为0 or +-10tick/价位，异常时候为+-10*Ntick/价位
        3. 5-8: 固定参数
            1. 5: 原始的成交量变更（基本都是很小的正数）
        4. 9: 成交量变更: 0-1(绝大部分集中在1e-3以下，没有成交量则为0，交易越久，越接近0)
        5. 10: 持仓量变化: -1-1
        6. 11-20: 相当于价位变更:
        """
        feature_delta = delta_trans.detach().clone()
        origin_delta = delta_origin.detach().clone()
        feature_delta[1:4] *= 10

        # 5-8放上原始有效特征
        feature_delta[5] = max(1e-6, data_tail[9].item()) if origin_delta[9].item() < 0 else max(1e-6, origin_delta[9].item())
        feature_delta[5] = torch.log2(feature_delta[5]) / 10

        feature_delta[9] = max(1e-6, feature_delta[9].item())
        feature_delta[9] = torch.log2(feature_delta[9]) / 10
        feature_delta[10] *= 2
        feature_delta[11:21] *= 10
        return feature_delta

    def insert(self, time: int, feature: torch.Tensor):
        if time <= self.__time_tail:
            return False
        self.__time_head = self.__time_tail
        self.__time_tail = time
        self.__time_delta[0] = math.log2((self.__time_tail - self.__time_head) / 500 + 1) / 10

        self.__feature_head = self.__feature_tail.detach().clone()
        self.__feature_head_trans = self.__feature_tail_trans.detach().clone()
        self.__feature_tail = feature.detach().clone()
        self.__feature_tail_trans = FeatureGenerator.__feature2trans(feature)
        self.__feature_delta = FeatureGenerator.__feature2delta(
            self.__feature_tail_trans - self.__feature_head_trans,
            self.__feature_tail - self.__feature_head,
            self.__feature_tail,
        )

        self.__feature = torch.cat([self.__time_delta, self.__feature_delta, self.__feature_tail])
        return True
    pass
