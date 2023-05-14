class ConnException(Exception):
    """TCP连接失败异常
    """
    pass


class ServiceNotFoundException(Exception):
    """未找到服务
    """
    pass


class ServiceExistException(Exception):
    """服务已存在
    """
    pass


class JsonIdException(Exception):
    """Json数据错误
    """
    pass


class FutureException(Exception):
    """未找到对应的future
    """
    pass


class ConnTimeoutError(Exception):
    """连接超时异常
    """
    pass
