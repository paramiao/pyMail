# pyMail v2.0 迁移指南

## 概述

pyMail v2.0 是从 Python 2 到 Python 3 的重大升级版本。本指南帮助你评估升级影响并顺利迁移。

---

## 快速评估：我需要修改代码吗？

### ✅ 无需修改（大多数用户）

如果你的代码符合以下情况，**升级后无需修改**：

```python
import pyMail

# 接收邮件
rml = pyMail.ReceiveMailDealer('user@gmail.com', 'password', 'imap.gmail.com')
rml.select('INBOX')
unread = rml.getUnread()

for num in unread[1][0].split(' '):
    if num:
        mail_info = rml.getMailInfo(num)
        print(mail_info['subject'])
        print(mail_info['body'])
        # 处理附件
        for att in mail_info['attachments']:
            with open(att['name'], 'wb') as f:
                f.write(att['data'])
```

**只要你**：
- 使用 `import pyMail`（而非 `import mailUtils`）
- 使用 `ReceiveMailDealer` 的基本方法
- 按示例处理返回值

---

### ⚠️ 需要小改（少数用户）

如果你使用了 `SendMailDealer`，需要补充 `port` 参数：

```python
# ❌ 旧代码（v1.x）
sml = pyMail.SendMailDealer('user@gmail.com', 'password', 'smtp.gmail.com')

# ✅ 新代码（v2.0）
sml = pyMail.SendMailDealer('user@gmail.com', 'password', 'smtp.gmail.com', 587, usettls=True)
# 或使用 SSL
sml = pyMail.SendMailDealer('user@gmail.com', 'password', 'smtp.gmail.com', 465, usettls=False)
```

---

### 🚫 会出错的情况（极少数）

如果你的代码有以下情况，升级会报错：

1. **错误的模块名**（Issue #8）
```python
# ❌ 这在 v1.x 就是错的，v2.0 仍然不工作
import pyMail
rml = mailUtils.ReceiveMailDealer(...)  # NameError

# ✅ 正确写法
import pyMail
rml = pyMail.ReceiveMailDealer(...)
```

2. **调用了 `reinitMailInfo()` 方法**（Issue #9，v1.x 就有 bug）
```python
# ❌ v1.x 语法错误，v2.0 已修复
sml.reinitMailInfo()  # v1.x: 会报错
# ✅ v2.0 已修复，可正常使用
```

3. **依赖 `getEmailFormat` 的错误返回**
```python
# ❌ v1.x 返回字符串表示错误
msg = rml.getEmailFormat(num)
if msg == "fetch error":  # 不推荐的用法
    print("获取失败")

# ✅ v2.0 抛出异常
try:
    msg = rml.getEmailFormat(num)
except pyMail.MailFetchError as e:
    print(f"获取失败: {e}")
```

---

## 破坏性变更详细说明

### 1. Python 版本要求

| 版本 | Python 支持 |
|------|-------------|
| v1.x | Python 2.7 only |
| v2.0 | Python 3.6+ |

**影响**：无法在 Python 2 环境运行

**迁移**：
- 升级到 Python 3.6+
- 或保持使用 v1.x（从 `python2` 分支获取）

---

### 2. SendMailDealer 构造函数

**变更原因**：原代码本就要求 `port` 参数，但 README 示例缺失，导致混淆

#### 变更对比
```python
# v1.x 实际签名（文档有误）
SendMailDealer(user, passwd, smtp, port, usettls=False)

# v2.0 签名（文档已修正）
SendMailDealer(user, passwd, smtp, port, usettls=False)  # 相同！
```

#### 常用端口
```python
# Gmail STARTTLS
SendMailDealer('user@gmail.com', 'app_password', 'smtp.gmail.com', 587, usettls=True)

# Gmail SSL
SendMailDealer('user@gmail.com', 'app_password', 'smtp.gmail.com', 465, usettls=False)

# 163邮箱
SendMailDealer('user@163.com', 'password', 'smtp.163.com', 465, usettls=False)

# QQ邮箱
SendMailDealer('user@qq.com', 'auth_code', 'smtp.qq.com', 587, usettls=True)
```

**迁移建议**：
- 如果你之前能成功发送邮件，说明已经传了 `port`，无需修改
- 如果参考 README 示例但发送失败，补充 `port` 参数即可

---

### 3. 错误处理方式

#### getEmailFormat
```python
# v1.x
msg = rml.getEmailFormat(num)
if msg == "fetch error":  # 返回字符串表示错误
    handle_error()

# v2.0（推荐）
try:
    msg = rml.getEmailFormat(num)
except pyMail.MailFetchError as e:
    handle_error(e)

# v2.0（兼容写法，但不推荐）
msg = rml.getEmailFormat(num)
if msg is None:  # 异常被捕获后可能返回 None
    handle_error()
```

**迁移建议**：
- 新代码使用 try-except
- 旧代码检查 `== "fetch error"` 的地方改为 try-except

---

### 4. 内部实现变更（不影响公共 API）

以下变更**不需要用户修改代码**，但需要了解：

#### 编码处理
- v1.x: 使用 `unicode` 类型和 `setdefaultencoding`
- v2.0: 使用 Python 3 原生 `str`，明确指定编码

**影响**：中文等非 ASCII 字符处理更稳定

#### 邮件解析
- v1.x: `message_from_string` 
- v2.0: `message_from_bytes`

**影响**：更正确地处理二进制邮件内容

#### 附件文件名（Issue #7 修复）
- v1.x: 直接使用解码后的文件名（可能包含路径）
- v2.0: 清洗非法字符，防止路径遍历

**影响**：
```python
# v1.x 可能的附件名（导致 IOError）
'\\webreq\\WebReqDocs\\file.pdf'  # Windows 路径

# v2.0 清洗后
'__webreq_WebReqDocs_file.pdf'    # 安全的文件名
```

---

## 新增功能（向后兼容）

以下功能可直接使用，不影响现有代码：

### 1. 获取所有邮件（Issue #4）

```python
# v2.0 新增
all_mails = rml.getAll()  # 获取所有邮件，不限于未读

# 等价于（这个在 v1.x 也能用）
all_mails = rml.search(None, 'ALL')
```

### 2. 便捷搜索方法（Issue #10）

```python
# v2.0 新增
subject_mails = rml.searchBySubject('发票')
sender_mails = rml.searchBySender('boss@company.com')
recent_mails = rml.searchByDateRange('01-Jan-2025')

# v1.x 需要手动构造（较繁琐）
subject_mails = rml.search(None, 'SUBJECT', '"发票"')
```

### 3. 自定义异常类型

```python
# v2.0 新增
try:
    rml = pyMail.ReceiveMailDealer(...)
except pyMail.MailAuthError:
    print("登录失败，检查用户名密码")
except pyMail.MailConnectionError:
    print("网络连接失败")
```

---

## 常见问题

### Q1: 我能同时使用 v1.x 和 v2.0 吗？
**A**: 可以，但不推荐
```python
# 不同 Python 环境
python2 -m pip install pymail==1.x  # 从 python2 分支
python3 -m pip install pymail==2.0  # 从 main 分支
```

### Q2: v2.0 还支持 Python 2 吗？
**A**: 不支持。Python 2 已于 2020 年停止维护，建议升级到 Python 3。

### Q3: 如何验证迁移成功？
**A**: 运行以下测试脚本：
```python
import pyMail
import sys

print(f"Python 版本: {sys.version}")
print(f"pyMail 导入成功: {hasattr(pyMail, 'ReceiveMailDealer')}")

# 尝试连接（替换为你的配置）
try:
    rml = pyMail.ReceiveMailDealer('user', 'pass', 'imap.example.com')
    print("✅ 连接成功")
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

### Q4: 为什么 Gmail 登录失败？
**A**: Gmail 不再支持"不够安全的应用"，需要：
1. 启用两步验证
2. 生成"应用专用密码"
3. 使用应用密码代替真实密码

参考：https://support.google.com/accounts/answer/185833

### Q5: 附件文件名变了怎么办？
**A**: v2.0 修复了 Issue #7，附件名会被清洗：
- 路径分隔符 `\` `/` → `_`
- 非法字符 `<>:"|?*` → `_`

如果你依赖特定的文件名格式，需要调整逻辑。

---

## 回滚方案

如果升级后遇到问题，可以临时回滚：

### 方法1：使用 python2 分支
```bash
git clone -b python2 https://github.com/paramiao/pyMail.git
```

### 方法2：指定旧版本
```bash
pip install pymail==1.x  # 如果发布了 v1.x 版本
```

### 方法3：本地保留旧文件
```bash
# 备份当前 pyMail.py
cp pyMail.py pyMail_v1.py

# 降级时恢复
cp pyMail_v1.py pyMail.py
```

---

## 逐步迁移策略（推荐）

如果你的项目较大，建议分步迁移：

### 第一步：环境准备
1. 升级到 Python 3.6+
2. 在测试环境安装 v2.0
3. 运行现有测试用例

### 第二步：代码审查
1. 搜索 `SendMailDealer` 调用，检查是否传 `port`
2. 搜索 `getEmailFormat` 调用，检查错误处理
3. 搜索 `== "fetch error"`，改为异常处理

### 第三步：灰度发布
1. 先在非关键服务上验证
2. 监控日志，确认无异常
3. 逐步推广到生产环境

### 第四步：利用新特性
1. 使用 `getAll()` 简化代码
2. 使用便捷搜索方法提升可读性
3. 利用异常类型细化错误处理

---

## 获取帮助

- **GitHub Issues**: https://github.com/paramiao/pyMail/issues
- **示例代码**: 参考 `example.py`
- **开发计划**: 参考 `DEVELOPMENT_PLAN.md`

---

## 总结

| 变更类型 | 影响范围 | 迁移难度 |
|---------|---------|---------|
| Python 版本 | 所有用户 | 简单（升级 Python） |
| SendMailDealer 端口 | 使用 SMTP 的用户 | 简单（补充参数） |
| 错误处理 | 检查错误返回值的用户 | 中等（改为异常） |
| 新增功能 | 无 | 无（可选使用） |

**大多数用户只需升级 Python 版本，无需修改代码即可使用 v2.0**
