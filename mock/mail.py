from attr import dataclass
from pytest_mock import MockerFixture

from ..src.dependency import mail


@dataclass
class MockMail:
    @staticmethod
    def mock_init(mocker: MockerFixture):
        mocker.patch(f'{mail.__name__}.Mail', new=MockMail)
        pass

    def send(self, *args, **kwds) -> None:
        print(f'单测-发送邮件-{args}-{kwds}')
        pass
    pass
