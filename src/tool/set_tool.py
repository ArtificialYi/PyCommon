class SetTargetManage:
    def __init__(self) -> None:
        self.__set_norm = set()
        self.__set_target = set()
        pass

    @property
    def added_set(self):
        return self.__set_norm

    @property
    def not_added_one(self):
        set_tmp = self.not_added_set
        return set_tmp.pop() if len(set_tmp) > 0 else None

    @property
    def not_added_set(self):
        return self.__set_target - self.__set_norm

    def add(self, contract):
        self.__set_norm.add(contract)
        self.__set_norm &= self.__set_target
        pass

    def set_target(self, contract_set: set):
        self.__set_target = contract_set
        self.__set_norm &= self.__set_target
        pass
    pass
