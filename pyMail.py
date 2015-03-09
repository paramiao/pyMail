# encoding: utf-8
import imaplib
import email
import sys
import smtplib
import logging
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.encoders import encode_base64
from email.header import Header

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.DEBUG,
                    format='%(filename)s[line:%(lineno)d] %(levelname)s: %(message)s',
                    stream=sys.stderr)


class ReceiveMailDealer:

    '''
    接收邮件类，使用IMAP4_SSL协议
    '''

    def __init__(self, username, password, server):
        '''
        初始化并登录邮箱
        :param username: 用户名
        :param password: 密码
        :param server:   IMAP邮箱服务器
        '''
        self.mail = imaplib.IMAP4_SSL(server)
        self.mail.login(username, password)
        self.select("INBOX")

    def showFolders(self):
        '''
        返回所有邮箱内的文件夹(list类型)
        '''
        return self.mail.list()

    def select(self, selector="INBOX"):
        '''
        选择收件箱，默认值"INBOX"
        '''
        return self.mail.select(selector)

    def search(self, charset, *criteria):
        '''
        搜索邮件(参照RFC文档http://tools.ietf.org/html/rfc3501#page-49)
        例如: m.search(None, "ALL") #搜素当前邮箱内所有邮件
        '''
        try:
            return self.mail.search(charset, *criteria)
        except:
            self.select("INBOX")
            return self.mail.search(charset, *criteria)

    def delete(self, ids=None):
        '''
        删除指定id列表的邮件
        :param ids: 想要删除邮件的id组成的list
        '''
        if ids:
            for n in ids:
                self.mail.store(n, '+FLAGS', '\\Deleted')
            self.mail.expunge()

    def getUnread(self):
        '''
        返回所有未读的邮件列表
        例如：['1 2 3 4']
        '''
        return self.search(None, "Unseen")

    def getEmailFormat(self, mail_id):
        '''
        以RFC822协议格式返回邮件详情的email对象(message object)
        :param id: 邮件id
        '''
        data = self.mail.fetch(mail_id, '(RFC822)')
        if data[0] == 'OK':
            return email.message_from_string(data[1][0][1])
        else:
            return None

    def getSenderInfo(self, msg):
        '''
        返回发送者信息的二元组（邮件称呼，邮件地址）
        :param msg: email对象（调用getemailFormat获得）
        '''
        name = email.Utils.parseaddr(msg["from"])[0]
        deName = email.Header.decode_header(name)[0]
        if deName[1] is not None:
            name = unicode(deName[0], deName[1])
        address = email.Utils.parseaddr(msg["from"])[1]
        return (name, address)

    def getReceiverInfo(self, msg):
        '''
        返回接受者的信息——元组（邮件称呼，邮件地址）
        :param msg: email对象（调用getemailFormat获得）
        '''
        name = email.Utils.parseaddr(msg["to"])[0]
        deName = email.Header.decode_header(name)[0]
        if deName[1] is not None:
            name = unicode(deName[0], deName[1])
        address = email.Utils.parseaddr(msg["to"])[1]
        return (name, address)

    def getSubjectContent(self, msg):
        '''
        返回邮件的主题
        :param msg: email对象（调用getemailFormat获得）
        '''
        deContent = email.Header.decode_header(msg['subject'])[0]
        if deContent[1] is not None:
            return unicode(deContent[0], deContent[1])
        return deContent[0]

    def parse_attachment(self, message_part):
        '''
        判断是否有附件，并解析（解析email对象的part），
        返回dict（"content_type"，"size"，""name"，"data"）或None
        :param message_part: email对象的part
        '''
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and \
                dispositions[0].lower() == "attachment"):

                file_data = message_part.get_payload(decode=True)
                attachment = {}
                attachment["content_type"] = message_part.get_content_type()
                attachment["size"] = len(file_data)
                deName = email.Header.decode_header(
                    message_part.get_filename())[0]
                name = deName[0]
                if deName[1] is not None:
                    name = unicode(deName[0], deName[1])
                attachment["name"] = name
                attachment["data"] = file_data
                return attachment
        return None

    def getMailInfo(self, mail_id):
        '''
        返回邮件的解析后信息部分
        返回dict（"subject"，"bobdy"，"html"，"from"，"to"，"attachments"）
        :param mail_id: 邮件id
        '''
        msg = self.getEmailFormat(mail_id)
        attachments = []
        body = None
        html = None
        for part in msg.walk():
            attachment = self.parse_attachment(part)
            if attachment:
                attachments.append(attachment)
            elif part.get_content_type() == "text/plain":
                if body is None:
                    body = ""
                body += part.get_payload(decode=True)
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = ""
                html += part.get_payload(decode=True)
        return {
            'subject': self.getSubjectContent(msg),
            'body': body,
            'html': html,
            'from': self.getSenderInfo(msg),
            'to': self.getReceiverInfo(msg),
            'attachments': attachments,
        }


#*********发送邮件部分(smtp)**********

class SendMailDealer:

    '''
    发送邮件类，使用smtp协议
    '''

    def __init__(self, user, passwd, smtp, port, usettls=False):
        '''
        :param user: 邮箱用户名
        :param passwd: 邮箱密码
        :param smtp: smtp服务器
        :param port: 端口
        :param userttls: 是否开启ttls
        '''
        self.mailUser = user
        self.mailPassword = passwd
        self.smtpServer = smtp
        self.smtpPort = port
        self.mailServer = smtplib.SMTP(self.smtpServer, self.smtpPort)
        self.mailServer.ehlo()
        if usettls:
            self.mailServer.starttls()
        self.mailServer.ehlo()
        self.mailServer.login(self.mailUser, self.mailPassword)
        self.msg = MIMEMultipart()

    def __del__(self):
        '''
        对象销毁时关闭mailserver
        '''
        self.mailServer.close()

    def reinitMailInfo(self):
        '''
        重新初始化邮件信息部分
        '''
        self.msg = MIMEMultipart()

    def setMailInfo(self, receiveUser, subject, text, text_type,
                    *attachmentFilePaths):
        '''
        设置邮件的基本信息
        :param receiveUser: 收件人
        :param subject:     主题
        :param text:        正文
        :param text_type:   正文类型（plain/html）
        :param *attachmentFilePaths:    附件路径
        '''
        self.msg['From'] = self.mailUser
        self.msg['To'] = receiveUser

        self.msg['Subject'] = subject
        self.msg.attach(MIMEText(text, text_type, 'utf-8'))
        for attachmentFilePath in attachmentFilePaths:
            if attachmentFilePath:
                self.msg.attach(self.getAttachmentFromFile(attachmentFilePath))

    # 自定义邮件正文信息（正文内容，正文格式html或者plain）
    def addTextPart(self, text, text_type):
        '''
        添加邮件正文信息
        :param text: 正文内容
        :param text_type: 正文格式(plain/html)
        '''
        self.msg.attach(MIMEText(text, text_type, 'utf-8'))

    # 增加附件（以流形式添加，可以添加网络获取等流格式）参数（文件名，文件流）
    def addAttachment(self, filename, filedata):
        '''
        直接添加附件，不通过文件
        :param filename: 附件名
        :param filedata: 附件内容
        '''
        part = MIMEBase('application', "octet-stream")
        part.set_payload(filedata)
        encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % str(Header(filename, 'utf8')))
        self.msg.attach(part)

    # 通用方法添加邮件信息（MIMETEXT，MIMEIMAGE,MIMEBASE...）
    def addPart(self, part):
        '''
        添加邮件信息的通用方法（MIMETEXT，MIMTIMAGE,MIMEBASE）
        '''
        self.msg.attach(part)

    # 发送邮件
    def sendMail(self):
        '''
        发送邮件
        '''
        if not self.msg['To']:
            logging.warning("没有收件人,请先设置邮件基本信息")
            return False
        try:
            self.mailServer.sendmail(
                self.mailUser, self.msg['To'], self.msg.as_string())
        except:
            logging.error("Sent email to %s failed!" % self.msg['To'])
            return False
        else:
            logging.debug('Sent email to %s success!' % self.msg['To'])
            return True

    # 通过路径添加附件
    def getAttachmentFromFile(self, attachmentFilePath):
        '''
        通过路径获取附件内容
        :param attachmentFilePath: 附件路径
        '''
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(attachmentFilePath, "rb").read())
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' %
                        str(Header(attachmentFilePath, 'utf8')))
        return part
