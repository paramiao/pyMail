## pyMail

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This is a mail helper, which helps you send and receive emails with Python more easily, especially for users who need Unicode support (e.g., Chinese, Japanese, Korean).

这是一个可以帮助你更好的使用 Python 收发邮件的项目，尤其是对 Unicode 的处理，可以完美支持中文。只需几行代码就可以去除繁琐的邮件解析、中文解析的操作。

### ⚠️ Version Notice | 版本说明

- **v2.0+**: Python 3.6+ (Recommended | 推荐)
- **v1.x**: Python 2.7 (No longer maintained | 不再维护，请使用 `python2` 分支)

### Description | 项目说明

**ReceiveMailDealer** is a class that helps you receive emails via IMAP and parse them automatically, with excellent Unicode/Chinese support:

**ReceiveMailDealer** 通过 IMAP 方式收取邮件，自动解析邮件内容，完美支持中文等 Unicode 字符：

```python
# 初始化接收邮件类
import pyMail

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

# v2.0 新增功能
# 获取所有邮件（不限于未读）
all_mails = rml.getAll()

# 按主题搜索
invoice_mails = rml.searchBySubject('发票')

# 按发件人搜索
boss_mails = rml.searchBySender('boss@company.com')

# 按日期范围搜索
recent_mails = rml.searchByDateRange('01-Jan-2025')
```

**SendMailDealer** is a class help you to send the mails, you can set the mail body very convenient, no matter text, html or attachments, just like below:
**SendMailDealer** 可以帮助你通过SMTP发送邮件，可以随意定制邮件的内容，包括纯文本，html或者附件，以下是示例代码：

```python
# 初始化发送邮件类
import pyMail

# Gmail with STARTTLS (port 587) - 推荐
sml = pyMail.SendMailDealer('mail_address', 'app_password', 'smtp.gmail.com', 587, usettls=True)

# 或使用 SSL (port 465)
# sml = pyMail.SendMailDealer('mail_address', 'app_password', 'smtp.gmail.com', 465, usettls=False)

# 设置邮件信息
sml.setMailInfo('recipient@example.com', '测试', '正文', 'plain', '/path/to/attachment.pdf')

# 发送邮件
sml.sendMail()

# 显式关闭连接（推荐）
sml.close()
```
## Installation | 安装

Install **pyMail** is very easy. Just download `pyMail.py` and import it:

安装 **pyMail** 非常简单，下载 `pyMail.py` 文件并导入即可：

```python
import pyMail
```

Or clone from GitHub | 或者从 GitHub 克隆：
```bash
git clone https://github.com/paramiao/pyMail.git
cd pyMail
# Copy pyMail.py to your project | 将 pyMail.py 复制到你的项目
```

## What's New in v2.0 | v2.0 新特性

### 🎉 New Features | 新功能
- **Python 3.6+ support** - Full migration to Python 3 | 完整迁移到 Python 3
- **Search functions** (Issue #4, #10) | 搜索功能：
  - `getAll()` - Get all emails, not just unread | 获取所有邮件，不限于未读
  - `searchBySubject(keyword)` - Search by subject | 按主题搜索
  - `searchBySender(email)` - Search by sender | 按发件人搜索
  - `searchByDateRange(since, before)` - Search by date range | 按日期范围搜索
- **Custom exceptions** - Better error handling | 自定义异常，更好的错误处理
- **Logging support** - Optional logging for debugging | 日志支持，便于调试

### 🐛 Bug Fixes | 问题修复
- **Fixed attachment filename handling** (Issue #7) - Properly sanitize filenames | 修复附件文件名处理，正确清洗路径和非法字符
- **Fixed `reinitMailInfo()`** (Issue #9) - Added missing `self` parameter | 添加缺失的 `self` 参数
- **Fixed example.py** (Issue #8) - Corrected `mailUtils` to `pyMail` | 修正模块名错误
- **Improved encoding handling** - Better support for various character encodings | 改进编码处理，更好地支持各种字符集

### ⚠️ Breaking Changes | 不兼容变更
- Requires Python 3.6+ | 需要 Python 3.6+
- `SendMailDealer.__init__()` now requires `port` parameter | 现在需要 `port` 参数

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions | 详细迁移说明请查看迁移指南。

## Common Issues | 常见问题

### Gmail Login Failed | Gmail 登录失败

Gmail no longer supports "less secure apps". You need to:
1. Enable 2-Step Verification
2. Generate an "App Password"
3. Use the app password instead of your real password

Gmail 不再支持"不够安全的应用"，需要：
1. 启用两步验证
2. 生成"应用专用密码"
3. 使用应用密码代替真实密码

Reference: https://support.google.com/accounts/answer/185833

### Connection Issues | 连接问题

**Common SMTP/IMAP ports:**
- **Gmail IMAP**: `imap.gmail.com:993`
- **Gmail SMTP (STARTTLS)**: `smtp.gmail.com:587`
- **Gmail SMTP (SSL)**: `smtp.gmail.com:465`
- **163**: `imap.163.com:993`, `smtp.163.com:465`
- **QQ**: `imap.qq.com:993`, `smtp.qq.com:587`

If using VPN, ensure SMTP/IMAP ports (587, 993, 465) are not blocked.

如果使用 VPN，确保 SMTP/IMAP 端口未被拦截。

## Contributors
paramiao:
* 微博 - http://weibo.com/paramiao
* Github - http://github.com/paramiao
* Twitter - http://twitter.com/paramiao

## License

MIT License

## Bugs and Feedback

- GitHub Issues: https://github.com/paramiao/pyMail/issues
- Email: paramiao#gmail.com

