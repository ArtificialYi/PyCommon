from torch import nn


class DropNorm(nn.Module):
    """带dropout的模型
    """
    def __init__(self, dropout: float = 0.5) -> None:
        super().__init__()
        self.drop = nn.Dropout(dropout)
        pass
    pass
