#!/usr/bin/env python2.7
# -*- coding: utf-8 -*
import pyMail
import getpass
import time
# 推荐使用qq邮箱
username = raw_input("User: ")
passwd = getpass.getpass()
smtp_server = raw_input("smtp server: ")
imap_server = raw_input("imap server: ")

# 初始化发送邮件类
sml = pyMail.SendMailDealer(username, passwd, smtp_server, 25)
# 设置邮件信息
sml.setMailInfo(username, u'标题', u'正文', 'plain', './README.md')
# 发送邮件
sml.sendMail()

# 初始化接收邮件类
rml = pyMail.ReceiveMailDealer(username, passwd, imap_server)
rml.select('INBOX')
# 延时2秒再读取邮件
time.sleep(2)
# 获取未读邮件列表
print(rml.getUnread())
#('OK',['1 2 3 4'])
# 遍历未读邮件
# print rml.search(None, 'ALL')
#()
for num in rml.getUnread()[1][0].split(' '):
    if num != '':
        mailInfo = rml.getMailInfo(num)
        print(rml.delete([num]))
        print(mailInfo['subject'])
        print(mailInfo['body'])
        print(mailInfo['html'])
        print(mailInfo['from'])
        print(mailInfo['to'])
        print(mailInfo['attachments'])
        # 遍历附件列表
        for attachment in mailInfo['attachments']:
            fileob = open(attachment['name'], 'wb')
            fileob.write(attachment['data'])
            fileob.close()
