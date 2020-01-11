#!/usr/bin/python
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


class Email(object):
    def __init__(self, server_account, server_passwd, server_addr='smtp.qq.com', server_port=465):
        self.server_account = server_account
        self.server_passwd = server_passwd
        self.server_addr = server_addr
        self.server_port = server_port

    def send_email(self, receiver_email, content):
        msg = MIMEText(content, "plain", 'utf-8')
        msg['From'] = formataddr(["test email", self.server_account])
        msg['To'] = formataddr(["receiver", receiver_email])
        msg['Subject'] = "test subject"

        try:
            server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server.login(self.server_account, self.server_passwd)
            server.sendmail(self.server_account, receiver_email, msg.as_string())
            server.quit()
        except Exception as e:
            self.lg.logger.info("send email failed: %s", e)


e = Email('youremail@qq.com', 'yourpasswd')
e.send_email('test@gmail.com', 'test content')

