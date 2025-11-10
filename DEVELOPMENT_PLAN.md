# pyMail v2.0 开发计划

## 项目背景

- **当前状态**: Python 2 项目，已停止维护多年
- **GitHub Issues**: 6 个未解决的问题（2015-2025）
- **用户需求**: 持续有开发者关注和使用
- **核心目标**: Python 3 迁移 + 修复关键 Bug + 增强易用性

## 版本规划

```
v1.x (当前)     → python2 分支（只读存档）
v2.0.0 (新版本) → main 分支（Python 3.6+）
```

---

## 优先级说明

- **P0 (Critical)**: 阻塞性问题，不修复则项目不可用
- **P1 (High)**: 用户强烈需求的功能，显著提升体验
- **P2 (Medium)**: 改善性优化，提升长期可维护性
- **P3 (Low)**: 锦上添花，可后续迭代

---

## P0 - 关键修复（必须完成）

### 1. 附件文件名处理 Bug 修复 ⭐️⭐️⭐️
**Issue**: #7  
**问题**: 附件文件名包含路径分隔符导致 IOError  
**影响**: 用户无法保存附件（核心功能失效）  
**根因**:
- 未使用 `os.path.basename` 提取文件名
- 未清洗 Windows 路径分隔符 `\`
- 未处理其他非法字符 `<>:"|?*`

**修复方案**:
```python
# pyMail.py line 92-98
1. 正确解码 Header 中的文件名（支持多段编码）
2. 使用 os.path.basename 去除路径
3. 替换路径分隔符: \ → _, / → _
4. 清洗非法文件名字符: <>:"|?* → _
5. 处理空文件名情况
```

**验证**: 测试包含路径的附件、中文文件名、特殊字符文件名  
**工时**: 1.5 小时

---

### 2. Python 3 完整迁移 ⭐️⭐️⭐️
**问题**: 当前代码无法在 Python 3 运行  
**影响**: 无法在现代 Python 环境使用

**修改清单**:

#### 2.1 导入路径修正
```python
# 旧代码 (Python 2)
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.encoders import encode_base64
import email.Utils
import email.Header

# 新代码 (Python 3)
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.encoders import encode_base64
from email import utils as email_utils
from email.header import decode_header, make_header, Header
```

#### 2.2 字节/字符串处理
```python
# IMAP fetch 返回 bytes，需使用
email.message_from_bytes(data[1][0][1])  # 而非 message_from_string

# 移除 Python 2 专有
reload(sys)  # 删除
sys.setdefaultencoding('utf8')  # 删除

# unicode → str (Python 3 原生支持)
```

#### 2.3 print 语句
```python
# 旧: print "xxx"
# 新: logger.debug("xxx") 或 print("xxx")
```

**验证**: 在 Python 3.8/3.9/3.10/3.11 环境运行  
**工时**: 2-3 小时

---

### 3. 基础 Bug 修复
**Issue**: #9, #8

#### 3.1 reinitMailInfo 缺少 self
```python
# 旧 (line 160)
def reinitMailInfo():
    self.msg = MIMEMultipart()

# 新
def reinitMailInfo(self):
    self.msg = MIMEMultipart()
```

#### 3.2 example.py 模块名错误
```python
# 旧
import pyMail
rml = mailUtils.ReceiveMailDealer(...)

# 新
import pyMail
rml = pyMail.ReceiveMailDealer(...)
```

#### 3.3 移除 debug print
```python
# pyMail.py line 96
print name  # 删除此行
```

**工时**: 15 分钟

---

### 4. SendMailDealer 构造函数修复
**问题**: README 示例与实际签名不符

**当前签名** (line 142):
```python
def __init__(self, user, passwd, smtp, port, usettls=False):
```

**修复**:
- 保持当前签名（需要 port）
- 更新 README 所有示例补充 port 参数
- 添加参数说明文档

**工时**: 30 分钟

---

## P1 - 功能增强（强烈建议完成）

### 5. 邮件搜索便捷方法 ⭐️⭐️
**Issue**: #4, #10  
**需求**: 
- 获取所有邮件（不只是未读）
- 按主题/发件人/日期搜索

**新增方法**:
```python
class ReceiveMailDealer:
    def getAll(self):
        """获取所有邮件列表"""
        return self.search(None, 'ALL')
    
    def searchBySubject(self, keyword):
        """按主题关键词搜索"""
        return self.search(None, 'SUBJECT', f'"{keyword}"')
    
    def searchBySender(self, sender_email):
        """按发件人搜索"""
        return self.search(None, 'FROM', sender_email)
    
    def searchByDateRange(self, since_date, before_date=None):
        """按日期范围搜索 (格式: DD-MMM-YYYY)"""
        criteria = ['SINCE', since_date]
        if before_date:
            criteria.extend(['BEFORE', before_date])
        return self.search(None, *criteria)
```

**工时**: 1 小时

---

### 6. 邮件解析健壮性改进 ⭐️⭐️
**问题**: bytes/str 混用、编码错误、Header 解码不完整

**改进点**:

#### 6.1 getEmailFormat 健壮性
```python
def getEmailFormat(self, num):
    data = self.mail.fetch(num, 'RFC822')
    if data[0] == 'OK':
        # 使用 message_from_bytes
        return email.message_from_bytes(data[1][0][1])
    else:
        # 抛出异常而非返回字符串
        raise MailFetchError(f"Failed to fetch email {num}: {data}")
```

#### 6.2 getMailInfo 正确解码
```python
def getMailInfo(self, num):
    msg = self.getEmailFormat(num)
    # ...
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            charset = part.get_content_charset() or 'utf-8'
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                try:
                    body += payload.decode(charset, errors='replace')
                except:
                    body += payload.decode('utf-8', errors='replace')
```

#### 6.3 Header 解码完整化
```python
def getSenderInfo(self, msg):
    from_header = msg.get('from', '')
    name, address = email_utils.parseaddr(from_header)
    # 使用 make_header 处理多段编码
    if name:
        decoded_name = str(make_header(decode_header(name)))
    else:
        decoded_name = ''
    return (decoded_name, address)
```

**工时**: 2 小时

---

### 7. 错误处理规范化 ⭐️
**问题**: print 报错、返回字符串表示错误

**改进**:
```python
# 新增自定义异常
class MailError(Exception):
    """邮件操作基础异常"""
    pass

class MailAuthError(MailError):
    """认证失败"""
    pass

class MailConnectionError(MailError):
    """连接失败"""
    pass

class MailFetchError(MailError):
    """邮件获取失败"""
    pass
```

**修改点**:
- `__init__`: 登录失败抛出 `MailAuthError`
- `getEmailFormat`: fetch 失败抛出 `MailFetchError`
- `search`: 失败时抛出明确异常
- 保留向后兼容：现有 print 改为 logging（不强制用户改代码）

**工时**: 1.5 小时

---

## P2 - 项目工程化（建议完成）

### 8. 项目结构与发布支持
**目标**: 支持 pip install

**添加文件**:

#### pyproject.toml
```toml
[project]
name = "pymail"
version = "2.0.0"
description = "Easy IMAP/SMTP mail library with Chinese support"
authors = [{name = "paramiao", email = "paramiao@gmail.com"}]
license = {text = "MIT"}
requires-python = ">=3.6"
readme = "README.md"
keywords = ["email", "imap", "smtp", "mail", "chinese"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
```

#### setup.py (兼容旧工具)
```python
from setuptools import setup
setup()
```

**工时**: 1 小时

---

### 9. 日志系统
**目标**: 可观测性

**实现**:
```python
import logging

logger = logging.getLogger('pymail')
logger.addHandler(logging.NullHandler())  # 默认不输出

# 用户可选配置
# logging.basicConfig(level=logging.DEBUG)
```

**工时**: 30 分钟

---

### 10. 基础测试框架
**目标**: 防止回归

**实现**:
```python
# tests/test_basic.py
def test_imports():
    """测试基本导入"""
    import pyMail
    assert hasattr(pyMail, 'ReceiveMailDealer')
    assert hasattr(pyMail, 'SendMailDealer')

def test_syntax():
    """测试语法正确性"""
    # 确保没有 Python 2 残留
```

**工时**: 1 小时

---

## P3 - 文档完善（可选）

### 11. 文档更新

#### README.md
- ⚠️ Python 3.6+ 要求声明
- 安装方式（`pip install` 支持后）
- Gmail App Password 说明
- 搜索方法示例
- 常见问题（VPN、编码、超时）

#### CHANGELOG.md
```markdown
# v2.0.0 (2025-11-XX)

## 破坏性变更
- 需要 Python 3.6+（不再支持 Python 2）
- `SendMailDealer.__init__` 现在必须提供 `port` 参数

## 新增功能
- 新增 `getAll()` 获取所有邮件 (#4)
- 新增 `searchBySubject/Sender/DateRange` 便捷搜索 (#10)
- 新增自定义异常类型

## Bug 修复
- 修复附件文件名包含路径分隔符导致无法保存 (#7)
- 修复 `reinitMailInfo` 缺少 self 参数 (#9)
- 修复 example.py 模块名错误 (#8)
- 修复 bytes/str 混用导致的编码问题

## 改进
- 完整 Python 3 支持
- 更健壮的 Header 解码
- 更清晰的错误提示
```

#### MIGRATION_GUIDE.md
（见下一部分）

**工时**: 2 小时

---

## 时间估算总计

| 阶段 | 工时 | 说明 |
|------|------|------|
| P0 - 关键修复 | 4.25h | 必须完成 |
| P1 - 功能增强 | 4.5h | 强烈建议 |
| P2 - 工程化 | 2.5h | 建议完成 |
| P3 - 文档 | 2h | 可选 |
| 测试验证 | 2h | 必须 |
| 分支管理与发布 | 1h | 必须 |
| **总计** | **16.25h** | 约 2-3 个工作日 |

---

## 风险评估

### 高风险项
1. **Python 3 迁移可能遗漏边缘情况**
   - 缓解: 在多个 Python 版本测试
   - 缓解: 保留 python2 分支供参考

2. **附件解码可能有未发现的边缘情况**
   - 缓解: 测试多种文件名格式（中文、特殊字符、路径）
   - 缓解: 添加 try-except 防御

### 中风险项
3. **API 变更导致现有用户代码失效**
   - 缓解: 最小化破坏性变更
   - 缓解: 提供清晰的迁移指南

4. **邮件解析编码问题**
   - 缓解: 使用 `errors='replace'` 作为兜底
   - 缓解: 保留原逻辑作为 fallback

### 低风险项
5. **新增搜索方法的 RFC3501 语法错误**
   - 缓解: 参考官方文档
   - 缓解: 保留底层 `search()` 方法供高级用户使用

---

## 测试验证计划

### 手动测试场景
1. ✅ Python 3.8/3.9/3.10/3.11 环境导入测试
2. ✅ 连接真实 IMAP/SMTP 服务器（Gmail/163）
3. ✅ 接收包含附件的邮件（测试 Issue #7）
4. ✅ 发送带附件的邮件
5. ✅ 搜索邮件（全部/主题/发件人）
6. ✅ 中文主题/正文/附件名测试

### 自动化测试
1. ✅ 语法检查（`python -m py_compile pyMail.py`）
2. ✅ 导入测试
3. ✅ 基础单元测试（不依赖真实服务器）

---

## 发布检查清单

### 代码
- [ ] 所有 P0 修复已完成
- [ ] 所有 P1 功能已实现
- [ ] 测试验证通过
- [ ] 无明显 TODO 或 FIXME

### 文档
- [ ] README.md 更新
- [ ] CHANGELOG.md 编写
- [ ] MIGRATION_GUIDE.md 提供
- [ ] example.py 验证可运行

### 版本控制
- [ ] python2 分支创建并推送
- [ ] main 分支更新
- [ ] 创建 v2.0.0 tag
- [ ] GitHub Release 发布

### Issues
- [ ] #4 关闭（getAll 实现）
- [ ] #7 关闭（附件修复）
- [ ] #8 关闭（example 修复）
- [ ] #9 关闭（reinitMailInfo 修复）
- [ ] #10 关闭（搜索功能）
- [ ] #5 添加文档说明后关闭

---

## 后续规划（v2.1+）

### 可能的改进方向
1. OAuth 支持（Gmail/Outlook）
2. 异步 API (asyncio)
3. 流式附件处理（大附件不占内存）
4. 更完善的 MIME 类型支持
5. 连接池与自动重连
6. 类型标注（Type Hints）

### 社区贡献
- 添加 CONTRIBUTING.md
- 设置 Issue/PR 模板
- 添加 Code of Conduct
