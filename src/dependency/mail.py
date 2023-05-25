import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from smtplib import SMTPServerDisconnected

from ..configuration.env import get_value_by_tag_and_field
from ..tool.map_tool import MapKey


class Mail:
    def __init__(self, smtp_server: str, port: int, sender_email: str, password: str) -> None:
        self.__smtp_server = smtp_server
        self.__port = port
        self.__sender_email = sender_email
        self.__password = password
        pass

    def __send_opt(self, receiver_email: str, text: str):
        try:
            server = smtplib.SMTP(self.__smtp_server, self.__port)
            server.starttls()
            server.login(self.__sender_email, self.__password)
            server.sendmail(self.__sender_email, receiver_email, text)
            server.quit()
        except SMTPServerDisconnected:
            server = smtplib.SMTP(self.__smtp_server, self.__port)
            server.starttls()
            server.login(self.__sender_email, self.__password)
            server.sendmail(self.__sender_email, receiver_email, text)
            server.quit()
            pass
        pass

    def send(self, receiver_email: str, title: str, content: str):
        message = MIMEMultipart()
        message["From"] = self.__sender_email
        message["To"] = receiver_email
        message["Subject"] = title
        message.attach(MIMEText(content))
        text = message.as_string()

        self.__send_opt(receiver_email, text)
        pass
    pass


class MailManage:
    @classmethod
    @MapKey(lambda _, *args: ':'.join(str(arg) for arg in args))
    def __get_mail(cls, smtp_server: str, port: int, sender_email: str, password: str):
        return Mail(smtp_server, port, sender_email, password)

    def __new__(cls, smtp_server: str, port: int, sender_email: str, password: str):
        return cls.__get_mail(smtp_server, port, sender_email, password)

    @staticmethod
    async def create(tag: str):  # pragma: no cover
        smtp_server, port, sender_email, password = await asyncio.gather(
            get_value_by_tag_and_field(tag, 'smtp'),
            get_value_by_tag_and_field(tag, 'port'),
            get_value_by_tag_and_field(tag, 'sender'),
            get_value_by_tag_and_field(tag, 'password'),
        )
        return MailManage(smtp_server, int(port), sender_email, password)
    pass
