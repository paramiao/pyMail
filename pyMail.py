# -*- coding: utf-8 -*-
import imaplib
import email
import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from email.header import Header, decode_header, make_header
from email import utils as email_utils

# 配置日志
logger = logging.getLogger('pymail')
logger.addHandler(logging.NullHandler())


# ========== 自定义异常 ==========
class MailError(Exception):
    """邮件操作基础异常"""
    pass


class MailAuthError(MailError):
    """认证失败异常"""
    pass


class MailConnectionError(MailError):
    """连接失败异常"""
    pass


class MailFetchError(MailError):
    """邮件获取失败异常"""
    pass


# ========== 接收邮件部分（IMAP）==========
# 处理接收邮件的类
class ReceiveMailDealer:

    # 构造函数(用户名，密码，imap服务器)
    def __init__(self, username, password, server):
        try:
            self.mail = imaplib.IMAP4_SSL(server)
            logger.info(f"Connected to IMAP server: {server}")
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server {server}: {e}")
            raise MailConnectionError(f"Cannot connect to {server}: {e}")
        
        try:
            self.mail.login(username, password)
            logger.info(f"Logged in as: {username}")
        except Exception as e:
            logger.error(f"Authentication failed for {username}: {e}")
            raise MailAuthError(f"Login failed: {e}")
        
        self.select("INBOX")
        
    # 返回所有文件夹
    def showFolders(self):
        return self.mail.list()
    
    # 选择收件箱（如"INBOX"，如果不知道可以调用showFolders）
    def select(self, selector):
        return self.mail.select(selector)

    # 搜索邮件(参照RFC文档http://tools.ietf.org/html/rfc3501#page-49)
    def search(self, charset, *criteria):
        try:
            return self.mail.search(charset, *criteria)
        except Exception as e:
            logger.warning(f"Search failed, retrying after selecting INBOX: {e}")
            try:
                self.select("INBOX")
                return self.mail.search(charset, *criteria)
            except Exception as e2:
                logger.error(f"Search failed after retry: {e2}")
                raise MailFetchError(f"Search failed: {e2}")

    # 返回所有未读的邮件列表（返回的是包含邮件序号的列表）
    def getUnread(self):
        """获取未读邮件列表"""
        return self.search(None, "Unseen")
    
    # 获取所有邮件列表 (Issue #4)
    def getAll(self):
        """获取所有邮件列表"""
        return self.search(None, 'ALL')
    
    # 按主题搜索 (Issue #10)
    def searchBySubject(self, keyword):
        """按主题关键词搜索邮件
        
        Args:
            keyword: 主题关键词
        
        Returns:
            搜索结果 (status, [mail_ids])
        """
        return self.search(None, 'SUBJECT', f'"{keyword}"')
    
    # 按发件人搜索 (Issue #10)
    def searchBySender(self, sender_email):
        """按发件人邮箱搜索邮件
        
        Args:
            sender_email: 发件人邮箱地址
        
        Returns:
            搜索结果 (status, [mail_ids])
        """
        return self.search(None, 'FROM', sender_email)
    
    # 按日期范围搜索
    def searchByDateRange(self, since_date, before_date=None):
        """按日期范围搜索邮件
        
        Args:
            since_date: 开始日期 (格式: DD-MMM-YYYY, 如 01-Jan-2023)
            before_date: 结束日期 (可选)
        
        Returns:
            搜索结果 (status, [mail_ids])
        """
        criteria = ['SINCE', since_date]
        if before_date:
            criteria.extend(['BEFORE', before_date])
        return self.search(None, *criteria)
    
    # 以RFC822协议格式返回邮件详情的email对象
    def getEmailFormat(self, num):
        """获取邮件的email对象
        
        Args:
            num: 邮件序号
        
        Returns:
            email.message.Message 对象
        
        Raises:
            MailFetchError: 获取邮件失败
        """
        try:
            data = self.mail.fetch(num, 'RFC822')
            if data[0] == 'OK' and data[1] and data[1][0]:
                # Python 3: 使用 message_from_bytes
                mail_data = data[1][0][1]
                if isinstance(mail_data, bytes):
                    return email.message_from_bytes(mail_data)
                else:
                    return email.message_from_string(mail_data)
            else:
                raise MailFetchError(f"Failed to fetch email {num}: {data}")
        except Exception as e:
            logger.error(f"Error fetching email {num}: {e}")
            raise MailFetchError(f"Failed to fetch email {num}: {e}")

    # 返回发送者的信息——元组（邮件称呼，邮件地址）
    def getSenderInfo(self, msg):
        """解析发件人信息
        
        Args:
            msg: email.message.Message 对象
        
        Returns:
            (name, address) 元组
        """
        from_header = msg.get('from', '')
        name, address = email_utils.parseaddr(from_header)
        
        # 使用 make_header 处理多段编码的 Header
        if name:
            try:
                decoded_name = str(make_header(decode_header(name)))
            except Exception as e:
                logger.warning(f"Failed to decode sender name, using raw: {e}")
                decoded_name = name
        else:
            decoded_name = ''
        
        return (decoded_name, address)

    # 返回接收者的信息——元组（邮件称呼，邮件地址）
    def getReceiverInfo(self, msg):
        """解析收件人信息
        
        Args:
            msg: email.message.Message 对象
        
        Returns:
            (name, address) 元组
        """
        to_header = msg.get('to', '')
        name, address = email_utils.parseaddr(to_header)
        
        # 使用 make_header 处理多段编码的 Header
        if name:
            try:
                decoded_name = str(make_header(decode_header(name)))
            except Exception as e:
                logger.warning(f"Failed to decode receiver name, using raw: {e}")
                decoded_name = name
        else:
            decoded_name = ''
        
        return (decoded_name, address)

    # 返回邮件的主题（参数msg是email对象，可调用getEmailFormat获得）
    def getSubjectContent(self, msg):
        """解析邮件主题
        
        Args:
            msg: email.message.Message 对象
        
        Returns:
            解码后的主题字符串
        """
        subject = msg.get('subject', '')
        if not subject:
            return ''
        
        try:
            # 使用 make_header 处理多段编码
            return str(make_header(decode_header(subject)))
        except Exception as e:
            logger.warning(f"Failed to decode subject, using raw: {e}")
            return subject

    # 判断是否有附件，并解析（解析email对象的part）
    # 返回字典（内容类型，大小，文件名，数据流）
    def parse_attachment(self, message_part):
        """解析附件
        
        Args:
            message_part: 邮件的一个 part
        
        Returns:
            附件字典 {content_type, size, name, data} 或 None
        """
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and dispositions[0].lower() == "attachment"):
                file_data = message_part.get_payload(decode=True)
                if not file_data:
                    return None
                
                attachment = {}
                attachment["content_type"] = message_part.get_content_type()
                attachment["size"] = len(file_data)
                
                # 获取并清洗文件名 (修复 Issue #7)
                filename = message_part.get_filename()
                if filename:
                    try:
                        # 正确解码多段编码的文件名
                        decoded_parts = decode_header(filename)
                        filename = ''.join([
                            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else str(part)
                            for part, encoding in decoded_parts
                        ])
                    except Exception as e:
                        logger.warning(f"Failed to decode filename: {e}")
                    
                    # 清洗文件名，防止路径遍历和非法字符 (Issue #7)
                    filename = os.path.basename(filename)  # 去除路径
                    filename = filename.replace('\\', '_').replace('/', '_')  # 替换路径分隔符
                    
                    # 清洗其他非法文件名字符
                    illegal_chars = '<>:"|?*'
                    for char in illegal_chars:
                        filename = filename.replace(char, '_')
                    
                    # 如果文件名为空或只有扩展名，生成默认名称
                    if not filename or filename.startswith('.'):
                        filename = f'attachment_{id(message_part)}{filename}'
                else:
                    # 无文件名，生成默认名称
                    ext = message_part.get_content_subtype()
                    filename = f'attachment_{id(message_part)}.{ext}'
                
                attachment["name"] = filename
                attachment["data"] = file_data
                logger.debug(f"Parsed attachment: {filename} ({len(file_data)} bytes)")
                
                return attachment
        return None

    # 返回邮件的解析后信息部分
    # 返回字典包含（主题，纯文本正文部分，html的正文部分，发件人元组，收件人元组，附件列表）
    def getMailInfo(self, num):
        """获取邮件完整信息
        
        Args:
            num: 邮件序号
        
        Returns:
            字典 {subject, body, html, from, to, attachments}
        """
        msg = self.getEmailFormat(num)
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
                # 正确处理 bytes 到 str 的转换
                payload = part.get_payload(decode=True)
                if payload:
                    if isinstance(payload, bytes):
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body += payload.decode(charset, errors='replace')
                        except Exception as e:
                            logger.warning(f"Failed to decode body with {charset}, using utf-8: {e}")
                            body += payload.decode('utf-8', errors='replace')
                    else:
                        body += payload
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = ""
                # 正确处理 bytes 到 str 的转换
                payload = part.get_payload(decode=True)
                if payload:
                    if isinstance(payload, bytes):
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            html += payload.decode(charset, errors='replace')
                        except Exception as e:
                            logger.warning(f"Failed to decode html with {charset}, using utf-8: {e}")
                            html += payload.decode('utf-8', errors='replace')
                    else:
                        html += payload
        
        return {
            'subject': self.getSubjectContent(msg),
            'body': body,
            'html': html,
            'from': self.getSenderInfo(msg),
            'to': self.getReceiverInfo(msg),
            'attachments': attachments,
        }


# ========== 发送邮件部分(smtp) ==========

class SendMailDealer:

    # 构造函数（用户名，密码，smtp服务器，端口，是否使用TLS）
    def __init__(self, user, passwd, smtp, port, usettls=False):
        """初始化SMTP连接
        
        Args:
            user: 邮箱用户名
            passwd: 密码或应用专用密码
            smtp: SMTP服务器地址
            port: 端口 (587用于STARTTLS, 465用于SSL)
            usettls: 是否使用STARTTLS (True for port 587, False for port 465)
        
        Raises:
            MailConnectionError: 连接失败
            MailAuthError: 认证失败
        """
        self.mailUser = user
        self.mailPassword = passwd
        self.smtpServer = smtp
        self.smtpPort = port
        
        try:
            self.mailServer = smtplib.SMTP(self.smtpServer, self.smtpPort)
            self.mailServer.ehlo()
            if usettls:
                self.mailServer.starttls()
                self.mailServer.ehlo()
            logger.info(f"Connected to SMTP server: {smtp}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to SMTP server {smtp}:{port}: {e}")
            raise MailConnectionError(f"Cannot connect to {smtp}:{port}: {e}")
        
        try:
            self.mailServer.login(self.mailUser, self.mailPassword)
            logger.info(f"Logged in as: {user}")
        except Exception as e:
            logger.error(f"Authentication failed for {user}: {e}")
            raise MailAuthError(f"Login failed: {e}")
        
        self.msg = MIMEMultipart()

    # 对象销毁时，关闭mailserver
    def __del__(self):
        """析构函数，关闭连接"""
        try:
            if hasattr(self, 'mailServer') and self.mailServer:
                self.mailServer.quit()
                logger.debug("SMTP connection closed")
        except Exception as e:
            logger.warning(f"Error closing SMTP connection: {e}")
    
    # 显式关闭连接（推荐使用）
    def close(self):
        """显式关闭SMTP连接"""
        try:
            if hasattr(self, 'mailServer') and self.mailServer:
                self.mailServer.quit()
                logger.info("SMTP connection closed")
        except Exception as e:
            logger.warning(f"Error closing SMTP connection: {e}")

    # 重新初始化邮件信息部分 (修复 Issue #9)
    def reinitMailInfo(self):
        """重新初始化邮件内容"""
        self.msg = MIMEMultipart()

    # 设置邮件的基本信息（收件人，主题，正文，正文类型html或者plain，可变参数附件路径列表）
    def setMailInfo(self, receiveUser, subject, text, text_type, *attachmentFilePaths):
        """设置邮件基本信息
        
        Args:
            receiveUser: 收件人邮箱
            subject: 邮件主题
            text: 邮件正文
            text_type: 正文类型 ('plain' 或 'html')
            *attachmentFilePaths: 附件文件路径列表
        """
        self.msg['From'] = self.mailUser
        self.msg['To'] = receiveUser
        self.msg['Subject'] = subject
        self.msg.attach(MIMEText(text, text_type, 'utf-8'))
        
        for attachmentFilePath in attachmentFilePaths:
            self.msg.attach(self.getAttachmentFromFile(attachmentFilePath))

    # 自定义邮件正文信息（正文内容，正文格式html或者plain）
    def addTextPart(self, text, text_type):
        """添加邮件正文部分
        
        Args:
            text: 正文内容
            text_type: 格式 ('plain' 或 'html')
        """
        self.msg.attach(MIMEText(text, text_type, 'utf-8'))
        

    # 增加附件（以流形式添加，可以添加网络获取等流格式）参数（文件名，文件流）
    def addAttachment(self, filename, filedata):
        """添加附件（流形式）
        
        Args:
            filename: 文件名
            filedata: 文件数据（bytes）
        """
        part = MIMEBase('application', "octet-stream")
        part.set_payload(filedata)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % str(Header(filename, 'utf-8')))
        self.msg.attach(part)

    # 通用方法添加邮件信息（MIMETEXT，MIMEIMAGE,MIMEBASE...）
    def addPart(self, part):
        """添加自定义邮件部分
        
        Args:
            part: MIME part 对象
        """
        self.msg.attach(part)

    # 发送邮件
    def sendMail(self):
        """发送邮件"""
        if not self.msg['To']:
            logger.error("No recipient specified")
            raise MailError("没有收件人,请先设置邮件基本信息")
        
        try:
            self.mailServer.sendmail(self.mailUser, self.msg['To'], self.msg.as_string())
            logger.info(f"Sent email to {self.msg['To']}")
            print(f'Sent email to {self.msg["To"]}')
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise MailError(f"发送邮件失败: {e}")

    # 通过路径添加附件
    def getAttachmentFromFile(self, attachmentFilePath):
        """从文件路径添加附件
        
        Args:
            attachmentFilePath: 附件文件路径
        
        Returns:
            MIMEBase 对象
        """
        part = MIMEBase('application', "octet-stream")
        with open(attachmentFilePath, "rb") as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        
        # 使用 basename 作为附件名，防止路径泄露
        filename = os.path.basename(attachmentFilePath)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % str(Header(filename, 'utf-8')))
        return part
