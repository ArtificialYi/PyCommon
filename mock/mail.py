

from pytest_mock import MockerFixture
from ..src.dependency import mail


class MockMail:
    @staticmethod
    def mock_init(mocker: MockerFixture):
        mock = mocker.patch(f'{mail.__name__}.MailManage.__new__')
        mock.return_value = MockMail()
        pass

    def send(self, *args, **kwds) -> None:
        pass
    pass
