# -*- coding: utf-8 -*-
import pyMail

# ========== 接收邮件示例 ==========

# 初始化接收邮件类 (修复 Issue #8: mailUtils -> pyMail)
rml = pyMail.ReceiveMailDealer('mail_address', 'mail_pwd', 'imap.gmail.com')
rml.select('INBOX')

# 获取未读邮件列表
print(rml.getUnread())  # ('OK', ['1 2 3 4'])

# 遍历未读邮件
for num in rml.getUnread()[1][0].split(' '):
    if num != '':
        mailInfo = rml.getMailInfo(num)
        print(mailInfo['subject'])
        print(mailInfo['body'])
        print(mailInfo['html'])
        print(mailInfo['from'])
        print(mailInfo['to'])
        # 遍历附件列表
        for attachment in mailInfo['attachments']:
            with open(attachment['name'], 'wb') as fileob:
                fileob.write(attachment['data'])

# ========== 新增功能示例 (v2.0) ==========

# 获取所有邮件 (Issue #4)
all_mails = rml.getAll()
print(f"Total mails: {len(all_mails[1][0].split())}")

# 按主题搜索 (Issue #10)
invoice_mails = rml.searchBySubject('发票')
print(f"Invoice mails: {invoice_mails}")

# 按发件人搜索 (Issue #10)
boss_mails = rml.searchBySender('boss@company.com')
print(f"Mails from boss: {boss_mails}")

# 按日期范围搜索
recent_mails = rml.searchByDateRange('01-Nov-2025')
print(f"Recent mails: {recent_mails}")

# ========== 发送邮件示例 ==========

# 初始化发送邮件类 (修复：补充 port 参数)
# Gmail with STARTTLS (port 587)
sml = pyMail.SendMailDealer('mail_address', 'app_password', 'smtp.gmail.com', 587, usettls=True)

# 设置邮件信息
sml.setMailInfo('recipient@example.com', '测试邮件', '这是邮件正文', 'plain', '/path/to/attachment.pdf')

# 发送邮件
sml.sendMail()

# 显式关闭连接（推荐）
sml.close()
