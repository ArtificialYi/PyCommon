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
