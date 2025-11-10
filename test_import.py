#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础导入和功能测试
用于验证 pyMail v2.0 的基本功能
"""

import sys

print("=" * 60)
print("pyMail v2.0 - Basic Import Test")
print("=" * 60)

# 测试导入
print("\n1. Testing import...")
try:
    import pyMail
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# 测试类是否存在
print("\n2. Testing classes...")
try:
    assert hasattr(pyMail, 'ReceiveMailDealer'), "ReceiveMailDealer not found"
    assert hasattr(pyMail, 'SendMailDealer'), "SendMailDealer not found"
    print("✅ Both classes found")
except AssertionError as e:
    print(f"❌ Class check failed: {e}")
    sys.exit(1)

# 测试异常类
print("\n3. Testing exception classes...")
try:
    assert hasattr(pyMail, 'MailError'), "MailError not found"
    assert hasattr(pyMail, 'MailAuthError'), "MailAuthError not found"
    assert hasattr(pyMail, 'MailConnectionError'), "MailConnectionError not found"
    assert hasattr(pyMail, 'MailFetchError'), "MailFetchError not found"
    print("✅ All exception classes found")
except AssertionError as e:
    print(f"❌ Exception check failed: {e}")
    sys.exit(1)

# 测试 ReceiveMailDealer 的新方法
print("\n4. Testing ReceiveMailDealer methods...")
try:
    methods = ['getUnread', 'getAll', 'searchBySubject', 'searchBySender', 'searchByDateRange']
    for method in methods:
        assert hasattr(pyMail.ReceiveMailDealer, method), f"{method} not found"
    print(f"✅ All {len(methods)} methods found")
except AssertionError as e:
    print(f"❌ Method check failed: {e}")
    sys.exit(1)

# 测试 SendMailDealer 的方法
print("\n5. Testing SendMailDealer methods...")
try:
    methods = ['setMailInfo', 'sendMail', 'addTextPart', 'addAttachment', 'reinitMailInfo', 'close']
    for method in methods:
        assert hasattr(pyMail.SendMailDealer, method), f"{method} not found"
    print(f"✅ All {len(methods)} methods found")
except AssertionError as e:
    print(f"❌ Method check failed: {e}")
    sys.exit(1)

# 测试 reinitMailInfo 是否有 self 参数（Issue #9）
print("\n6. Testing reinitMailInfo signature (Issue #9 fix)...")
try:
    import inspect
    sig = inspect.signature(pyMail.SendMailDealer.reinitMailInfo)
    params = list(sig.parameters.keys())
    assert 'self' in params, "reinitMailInfo missing 'self' parameter"
    print("✅ reinitMailInfo has 'self' parameter")
except Exception as e:
    print(f"❌ Signature check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed!")
print("=" * 60)
print("\nPython version:", sys.version)
print("\nReady to use pyMail v2.0")
print("\nNote: Connection tests require valid IMAP/SMTP credentials")
print("=" * 60)
