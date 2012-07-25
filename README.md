## pyMail

This is a mail helper, which help you more easy to send or receive mail with python, especially for the user who lives in a 'unicode' country, e.g. China.

这是一个可以帮助你更好的使用python收发邮件的项目，尤其是对unicode的处理，可以完美支持中文。只需几行代码就可以去除繁琐的邮件解析，中文解析的操作。

### Description

**ReceiveMailDealer** is a class help you to receive mail.It could do the work that use IMAP to receive the mails, and
use 'email' to parse the mail. So you can get the mail infomation directly, just like below:
**ReceiveMailDealer** 通过IMAP的方式收取邮件，它会自动收取，并且解析邮件的内容，包括对中文的处理，例如下面：

```python
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
```

**SendMailDealer** is a class help you to send the mails, you can set the mail body very convenient, no matter text, html or attachments, just like below:
**SendMailDealer** 可以帮助你通过SMTP发送邮件，可以随意定制邮件的内容，包括纯文本，html或者附件，以下是示例代码：

```python
#初始化发送邮件类
sml = mailUtils.SendMailDealer('mail_address','mail_pwd','smtp.gmail.com')
#设置邮件信息
sml.setMailInfo('paramiao#gmail.com','测试','正文','plain','/home/paramiao/resume.html')
#发送邮件
sml.sendMail()
#除了上述之外还有其他方法随意添加
```
## Installation

Install **pyMail** is very easy. Just edit your file adding the following:

```python
import pyMail
```


## Contributors
paramiao:
* 微博 - http://weibo.com/paramiao
* Github - http://github.com/paramiao
* Twitter - http://twitter.com/paramiao

## Bugs and Feedback

please mailto 'paramiao#gmail.com'

