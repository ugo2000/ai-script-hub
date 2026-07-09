# -*- coding: utf-8 -*-
"""支付宝当面付配置
支持 Docker 环境：通过环境变量传入私钥内容
"""

import os

# ===== 从支付宝开放平台获取 =====
ALIPAY_APP_ID = "2021006170643597"

# 应用私钥
# 本地开发：从 app_private_key.pem 读取
# 云环境（Zeabur/Railway）：从环境变量 ALIPAY_PRIVATE_KEY 读取
APP_PRIVATE_KEY_PATH = "app_private_key.pem"
APP_PRIVATE_KEY_ENV = os.environ.get("ALIPAY_PRIVATE_KEY", "")

# 支付宝公钥
# 云环境可从 ALIPAY_PUBLIC_KEY 环境变量覆盖
ALIPAY_PUBLIC_KEY = os.environ.get(
    "ALIPAY_PUBLIC_KEY",
    """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApGjsPF5VD/KKYzMD5F3zV6sSOAA7fwXxyf1hMLUT48gEOB9TBWdQuHNqGGor7+z9POmAAPqb5v3jTW8LOp0VKahLWuffbxqZjOVd2Xb7sML1Hx2mKBrIb8a64MEAzwl3ztNTMcc25mDEq9Kpkg9frBfswDUodKtkZ4lptEGSH+IudCPULUwYAozkt6pVQwcgv/K4h6L8QK5l83LcHeHuUgltSJqxXlwY8DuVToR/iuzKvrh2wkodCmiRVgsjT5NDdBcpo1T8JQMc6T1TvRu1ELS7sVnz5La/2E6Ihkg8VTAoWE4cdCSHcWJJzkA9SbiG645pdWdhP2F9INiI7yVGPwIDAQAB
-----END PUBLIC KEY-----"""
)

# ===== 回调地址 =====
BASE_URL = os.environ.get("BASE_URL", "https://www.jugongchang.icu")
NOTIFY_URL = f"{BASE_URL}/api/alipay/notify"

# ===== 当面付参数 =====
TRADE_TIMEOUT_MINUTES = 30
