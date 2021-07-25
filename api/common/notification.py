import smtplib
from email.mime.text import MIMEText
from email.header import Header
import logging

logger = logging.getLogger('log')

class EmailSender:
    """
        邮件发送
        EmailSender(**kwargs).sendMail(subject, content)
    """

    def __init__(self, **kwargs):
        # 第三方 SMTP 服务
        self.mailHost = kwargs.get("mailHost", "")  # 设置服务器
        self.mailUser = kwargs.get("mailUser", "")  # 用户名
        self.mailPassword = kwargs.get("mailPassword", "")  # 口令
        self.sender = kwargs.get("sender", "")
        self.receivers = kwargs.get("receivers", "")  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    def msgConfig(self, subject, content):
        # 内容
        message = MIMEText(content, 'plain', 'utf-8')
        # 主题
        message['Subject'] = Header(subject, "utf-8").encode()
        # 发送方
        message['From'] = Header(self.sender, 'utf-8')
        # 接收方
        message['To'] = Header(",".join(self.receivers), 'utf-8')
        return message

    def sendMail(self, subject, content):
        message = self.msgConfig(subject, content)
        data = {"code":1001}
        try:
            smtpObj = smtplib.SMTP()
            smtpObj.connect(self.mailHost, 25)  # 25 为 SMTP 端口号
            smtpObj.login(self.mailUser, self.mailPassword)
            smtpObj.sendmail(self.sender, self.receivers, message.as_string())
            logger.info("邮件发送成功")
            data["code"] = 1000
            data["data"] = "邮件发送成功"
        except smtplib.SMTPException as e:
            logger.error("Error: 无法发送邮件：%s" % e)
            data["data"] = "Error: 无法发送邮件"
        except Exception as e:
            logger.error("邮件发送失败，异常原因：%s" % e)
            data["data"] = "邮件发送失败，异常原因：%s" % e
        return data

if __name__ == '__main__':
    kwargs = {"mailHost": "smtp.qq.com", "mailUser": "971567069@qq.com", "mailPassword": "nbvgfdcukqjjbbaa",
              "sender": "971567069@qq.com", "receivers": ['971567069@qq.com']}
    EmailSender(**kwargs).sendMail("朱占豪测试主题", "朱占豪测试内容")
