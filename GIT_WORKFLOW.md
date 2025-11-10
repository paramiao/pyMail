# Git 分支管理与发布流程

本文档说明如何创建 Python 2 分支和发布 v2.0.0

## 当前状态

- ✅ 代码已完全重构（P0 + P1）
- ✅ 所有测试通过
- ✅ 文档已更新
- ✅ 旧代码已备份为 `pyMail_python2_backup.py`

## 步骤 1: 创建 python2 分支保留旧代码

### 1.1 检查当前状态
```bash
cd /Users/paramiao/development/pyMail
git status
```

### 1.2 提交当前所有新文件（临时提交到 main）
```bash
# 查看变更
git status

# 添加所有新文件
git add DEVELOPMENT_PLAN.md MIGRATION_GUIDE.md CHANGELOG.md test_import.py GIT_WORKFLOW.md

# 临时提交（稍后会整理）
git commit -m "WIP: v2.0 development files"
```

### 1.3 回退到旧代码并创建 python2 分支
```bash
# 找到最后一个 Python 2 的提交（v2.0 之前）
git log --oneline

# 假设最后的 Python 2 提交是 <commit_hash>
# 从那个提交创建 python2 分支
git branch python2 <commit_hash>

# 或者如果你想用当前备份的旧代码
git checkout -b python2-archive

# 恢复旧代码
mv pyMail.py pyMail_v2.py
mv pyMail_python2_backup.py pyMail.py

# 提交 python2 分支
git add pyMail.py
git commit -m "Archive Python 2 version as python2 branch

This branch preserves the Python 2.7 compatible version.
No longer maintained. Users should migrate to v2.0+ (Python 3.6+)
"

# 推送 python2 分支
git push -u origin python2-archive
```

## 步骤 2: 清理 main 分支并提交 v2.0

### 2.1 切换回 main 分支
```bash
git checkout main

# 确保使用新代码
mv pyMail_v2.py pyMail.py  # 如果需要
```

### 2.2 清理临时文件
```bash
# 删除备份文件
rm pyMail_python2_backup.py  # 已在 python2 分支保留

# 查看要提交的文件
git status
```

### 2.3 提交 v2.0 到 main 分支
```bash
# 添加所有修改
git add -A

# 提交 v2.0
git commit -m "Release v2.0.0 - Python 3 migration and feature enhancements

Major Changes:
- Full Python 3.6+ support (drop Python 2.7)
- Fixed critical attachment filename bug (#7)
- Added search functions: getAll(), searchBySubject(), searchBySender() (#4, #10)
- Fixed reinitMailInfo() missing self parameter (#9)
- Fixed example.py module name (#8)
- Improved encoding handling and error messages
- Added custom exception classes
- Added logging support

Breaking Changes:
- Requires Python 3.6+
- SendMailDealer.__init__() now requires port parameter

See CHANGELOG.md for full details.

Resolves: #4, #7, #8, #9, #10
"
```

### 2.4 创建 v2.0.0 标签
```bash
# 创建标签
git tag -a v2.0.0 -m "Release v2.0.0

Python 3 migration with bug fixes and new features.

Highlights:
- Python 3.6+ support
- Fixed attachment handling (#7)
- Search functions (#4, #10)
- Better error handling

See CHANGELOG.md for details.
"

# 查看标签
git tag -l
git show v2.0.0
```

### 2.5 推送到远程
```bash
# 推送 main 分支
git push origin main

# 推送标签
git push origin v2.0.0

# 或推送所有标签
git push origin --tags
```

## 步骤 3: GitHub Release

### 3.1 在 GitHub 创建 Release

访问: https://github.com/paramiao/pyMail/releases/new

#### Release 信息:
- **Tag**: v2.0.0
- **Title**: pyMail v2.0.0 - Python 3 Migration
- **Description**: (复制以下内容)

```markdown
# pyMail v2.0.0 - Python 3 Migration 🎉

## ⚠️ Breaking Changes
- **Requires Python 3.6+** (Python 2 is no longer supported)
- Python 2 users: please use the `python2` branch (v1.x)
- `SendMailDealer.__init__()` now requires `port` parameter

## 🎉 New Features
- **Search functions** (#4, #10):
  - `getAll()` - Get all emails
  - `searchBySubject(keyword)` - Search by subject
  - `searchBySender(email)` - Search by sender
  - `searchByDateRange(since, before)` - Search by date
- **Custom exceptions** for better error handling
- **Logging support** for debugging

## 🐛 Bug Fixes
- **Fixed attachment filename handling** (#7) - Sanitize filenames with paths/illegal characters
- **Fixed `reinitMailInfo()`** (#9) - Added missing `self` parameter
- **Fixed example.py** (#8) - Corrected module name from `mailUtils` to `pyMail`
- **Improved encoding** - Better support for various character sets

## 📚 Documentation
- Updated README with Python 3 examples
- Added [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- Added [CHANGELOG.md](CHANGELOG.md)
- Added common issues (Gmail App Passwords, VPN, ports)

## 🚀 Migration
Most users only need to:
1. Upgrade to Python 3.6+
2. Add `port` parameter to `SendMailDealer`
3. Enjoy new features!

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

## 🙏 Thanks
Thanks to all contributors who reported issues: @raymondlu31, @fanpei91, @xuechaoke, @huizhou-jixi-zhangxin, @vanpersiexp

---

**Full Changelog**: [CHANGELOG.md](CHANGELOG.md)
```

### 3.2 附件（可选）
- 可以附加 `pyMail.py` 作为独立文件供下载

### 3.3 发布
- 勾选 "Set as the latest release"
- 点击 "Publish release"

## 步骤 4: 关闭 Issues

在 GitHub 上关闭以下 Issues，并添加评论：

### Issue #4
```
Fixed in v2.0.0! 🎉

Added `getAll()` method to get all emails:
```python
all_mails = rml.getAll()
```

See [CHANGELOG.md](../CHANGELOG.md) for details.
```

### Issue #7
```
Fixed in v2.0.0! 🎉

Attachment filenames are now properly sanitized:
- Removes path separators (\ and /)
- Cleans illegal characters (<>:"|?*)
- Uses os.path.basename() to prevent directory traversal

Your example should now work correctly!
```

### Issue #8
```
Fixed in v2.0.0! 🎉

Corrected `mailUtils` to `pyMail` in example.py. Thanks for catching this!
```

### Issue #9
```
Fixed in v2.0.0! 🎉

Added missing `self` parameter to `reinitMailInfo()`:
```python
def reinitMailInfo(self):  # Now correct!
    self.msg = MIMEMultipart()
```
```

### Issue #10
```
Fixed in v2.0.0! 🎉

Added multiple search functions:
- `searchBySubject(keyword)` - Search by subject
- `searchBySender(email)` - Search by sender  
- `searchByDateRange(since, before)` - Search by date

Example:
```python
invoice_mails = rml.searchBySubject('发票')
boss_mails = rml.searchBySender('boss@company.com')
```

See [README.md](../README.md) for more examples.
```

### Issue #5 (可选关闭或添加说明)
```
Documented in v2.0.0

This is a network/VPN configuration issue. Added documentation in README:
- Common SMTP/IMAP ports
- VPN troubleshooting tips

See [README.md#common-issues](../README.md#common-issues--常见问题)
```

## 步骤 5: 更新 README Badge（可选）

如果需要，更新 README.md 中的 badge 链接指向正确的版本。

## 验证清单

- [ ] python2 分支已创建并推送
- [ ] main 分支包含所有 v2.0 代码
- [ ] v2.0.0 标签已创建并推送
- [ ] GitHub Release 已发布
- [ ] 所有相关 Issues 已关闭
- [ ] README.md 正确显示
- [ ] CHANGELOG.md 可访问

## 后续维护

### Python 2 分支 (python2)
- 标记为 "No longer maintained"
- 在 README 中添加弃用说明
- 不接受新功能请求
- 仅接受关键安全修复（如果必要）

### Main 分支 (v2.0+)
- 积极维护
- 接受 bug 修复和功能请求
- 遵循语义化版本（Semantic Versioning）

## 回滚计划（如果需要）

如果发现严重问题：
```bash
# 删除 v2.0.0 标签
git tag -d v2.0.0
git push origin :refs/tags/v2.0.0

# 在 GitHub 删除 Release

# 回退 main 分支
git revert <commit_hash>
git push origin main
```

---

**准备发布！** 🚀
