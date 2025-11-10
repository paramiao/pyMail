# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-11-10

### 🎉 New Features

#### Search & Filter (Issues #4, #10)
- **`getAll()`** - Get all emails, not limited to unread messages
- **`searchBySubject(keyword)`** - Search emails by subject keyword
- **`searchBySender(email)`** - Search emails by sender address
- **`searchByDateRange(since, before)`** - Search emails by date range (RFC3501 format: DD-MMM-YYYY)

#### Error Handling
- **Custom exception classes**:
  - `MailError` - Base exception for all mail operations
  - `MailAuthError` - Authentication failures
  - `MailConnectionError` - Connection failures
  - `MailFetchError` - Email fetching failures
- Exceptions now provide meaningful error messages instead of returning error strings

#### Logging Support
- Added optional logging using Python's `logging` module
- Logger name: `'pymail'`
- Default: `NullHandler` (no output unless configured by user)
- Users can enable logging: `logging.basicConfig(level=logging.DEBUG)`

#### Developer Experience
- Added docstrings to all public methods
- Better function signatures and return type documentation
- Added `close()` method for explicit connection cleanup

### 🐛 Bug Fixes

#### Critical
- **Fixed attachment filename handling** (Issue #7)
  - Remove path separators (`\`, `/`) from attachment filenames
  - Sanitize illegal filename characters (`<>:"|?*`)
  - Use `os.path.basename()` to prevent directory traversal
  - Properly decode multi-part encoded filenames
  - Generate default names for empty/invalid filenames

#### Important
- **Fixed `reinitMailInfo()` method** (Issue #9)
  - Added missing `self` parameter (was causing `NameError`)

- **Fixed example.py** (Issue #8)
  - Corrected `mailUtils` to `pyMail` (was incorrect module name)
  - Updated all examples to Python 3 syntax

- **Improved email parsing**:
  - Fixed `bytes`/`str` mixing issues in Python 3
  - Properly decode email body using `get_content_charset()`
  - Handle decoding errors gracefully with `errors='replace'`
  - Use `email.message_from_bytes()` instead of `message_from_string()`

- **Better header decoding**:
  - Use `make_header()` for multi-segment encoded headers
  - Support complex header encodings (e.g., mixed UTF-8 and GB2312)
  - Graceful fallback for malformed headers

#### Minor
- Fixed `__del__` method to use `quit()` instead of `close()` for SMTP
- Added defensive checks in destructor to prevent errors
- Removed debug `print` statement from `parse_attachment()`

### ⚡ Improvements

#### Python 3 Migration
- **Full Python 3.6+ support**
- Removed Python 2 dependencies:
  - Removed `reload(sys)` and `sys.setdefaultencoding()`
  - Replaced `unicode` type with `str`
  - Updated all `print` statements to `print()` functions
- Updated import paths:
  - `email.MIMEMultipart` → `email.mime.multipart.MIMEMultipart`
  - `email.MIMEBase` → `email.mime.base.MIMEBase`
  - `email.MIMEText` → `email.mime.text.MIMEText`
  - `email.Utils` → `email.utils`
  - `email.Header` → `email.header`
  - `email.encoders.encode_base64` → `email.encoders.encode_base64`

#### Code Quality
- Consistent code style and formatting
- Better error messages with context
- Safer file operations (using `with` statements in examples)
- More robust exception handling with specific exception types

### ⚠️ Breaking Changes

#### Python Version
- **Requires Python 3.6+**
- Python 2.7 is no longer supported
- For Python 2 users, please use the `python2` branch (v1.x)

#### API Changes
- **`SendMailDealer.__init__()`** now requires `port` parameter:
  ```python
  # Old (incorrect, was causing issues)
  SendMailDealer(user, passwd, smtp)
  
  # New (correct)
  SendMailDealer(user, passwd, smtp, port, usettls=False)
  ```
  - Port 587: Use with `usettls=True` (STARTTLS)
  - Port 465: Use with `usettls=False` (SSL)

#### Behavior Changes
- `getEmailFormat()` now raises `MailFetchError` instead of returning `"fetch error"` string
- Connection failures raise exceptions instead of printing errors
- Authentication failures raise `MailAuthError` with detailed messages

### 📚 Documentation

- Updated README.md with Python 3 examples
- Added version notice (v2.0 vs v1.x)
- Added common issues section (Gmail App Passwords, VPN, ports)
- Added "What's New in v2.0" section
- Created MIGRATION_GUIDE.md with step-by-step migration instructions
- Created DEVELOPMENT_PLAN.md for contributors
- Updated example.py with new features and correct syntax

### 🔄 Migration Path

For most users, migration is simple:
1. Upgrade to Python 3.6+
2. If using `SendMailDealer`, add the `port` parameter
3. Update error handling from string checks to exception handling (optional)

See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for details.

### 🙏 Acknowledgments

Special thanks to all users who reported issues:
- @raymondlu31 for reporting Issue #7 (attachment handling)
- @fanpei91 for requesting Issue #4 (get all emails)
- @xuechaoke for requesting Issue #10 (search functions)
- @huizhou-jixi-zhangxin for reporting Issue #8 and #9 (code errors)
- @vanpersiexp for raising Issue #5 (VPN connection, documented)

---

## [1.x] - Legacy (Python 2)

Previous versions for Python 2.7 are preserved in the `python2` branch.
No longer maintained.

For historical changes, please refer to the `python2` branch.
