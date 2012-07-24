# -*- coding: utf-8 -*
import pyMail

#初始化接收邮件类
rml = mailUtils.ReceiveMailDealer('mail_address','mail_pwd','imap.gmail.com')
rml.select('INBOX')
#获取未读邮件列表
print rml.getUnread()#('OK',['1 2 3 4'])
#遍历未读邮件
for num in rml.getUnread()[1][0].split(' '):
    if num != '':   
        mailInfo = rml.getMailInfo(num)
        print mailInfo['subject']
        print mailInfo['body']
        print mailInfo['html']
        print mailInfo['from']
        print mailInfo['to']
        #遍历附件列表
        for attachment in mailInfo['attachments']:
            fileob = open(attachment['name'],'wb')
            fileob.write(attachment['data'])
            fileob.close()

#初始化发送邮件类
sml = mailUtils.SendMailDealer('mail_address','mail_pwd','smtp.gmail.com')
#设置邮件信息
sml.setMailInfo('paramiao@gmail.com','测试','正文','plain','/home/paramiao/resume.html')
#发送邮件
sml.sendMail()
