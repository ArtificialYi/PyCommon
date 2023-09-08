import asyncio
import smtplib

from attr import dataclass, fields, ib
from smtplib import SMTPServerDisconnected
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..tool.base import BaseTool
from ..tool.map_tool import MapKey
from ..configuration.norm.env import get_value_by_tag_and_field


@dataclass
class Mail:
    smtp: str
    port: int = ib(converter=int)
    sender: str
    password: str = ib(repr=False)

    def __send_opt(self, receiver_email: str, text: str):
        try:
            server = smtplib.SMTP(self.smtp, self.port)
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver_email, text)
            server.quit()
        except SMTPServerDisconnected:
            server = smtplib.SMTP(self.smtp, self.port)
            server.starttls()
            server.login(self.sender, self.password)
            server.sendmail(self.sender, receiver_email, text)
            server.quit()
            pass
        pass

    def send(self, receiver_email: str, title: str, content: str):
        message = MIMEMultipart()
        message["From"] = self.sender
        message["To"] = receiver_email
        message["Subject"] = title
        message.attach(MIMEText(content))
        text = message.as_string()

        self.__send_opt(receiver_email, text)
        pass
    pass


class MailManage:
    @staticmethod
    @MapKey(BaseTool.return_self)
    async def __get_mail(tag: str):
        return Mail(*(await asyncio.gather(
            get_value_by_tag_and_field(tag, attr.name)
            for attr in fields(Mail)
        )))

    def __new__(cls, tag: str):
        return cls.__get_mail(tag)
    pass
