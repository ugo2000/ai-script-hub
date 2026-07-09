# -*- coding: utf-8 -*-
"""支付宝当面付配置
使用前创建 alipay_keys.py（已 gitignore），填入真实密钥
"""

# ===== 从支付宝开放平台获取 =====
ALIPAY_APP_ID = "2021006170643597"

# 应用私钥（gen_alipay_keys.py 生成的 app_private_key.pem 内容）
APP_PRIVATE_KEY_PATH = "app_private_key.pem"

# 支付宝公钥（支付宝开放平台 -> 接口加签 -> 查看支付宝公钥，复制粘贴到这里）
ALIPAY_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApGjsPF5VD/KKYzMD5F3zV6sSOAA7fwXxyf1hMLUT48gEOB9TBWdQuHNqGGor7+z9POmAAPqb5v3jTW8LOp0VKahLWuffbxqZjOVd2Xb7sML1Hx2mKBrIb8a64MEAzwl3ztNTMcc25mDEq9Kpkg9frBfswDUodKtkZ4lptEGSH+IudCPULUwYAozkt6pVQwcgv/K4h6L8QK5l83LcHeHuUgltSJqxXlwY8DuVToR/iuzKvrh2wkodCmiRVgsjT5NDdBcpo1T8JQMc6T1TvRu1ELS7sVnz5La/2E6Ihkg8VTAoWE4cdCSHcWJJzkA9SbiG645pdWdhP2F9INiI7yVGPwIDAQAB
-----END PUBLIC KEY-----"""

# ===== 回调地址 =====
# 当面付不需要同步跳转，只需要异步通知
# 需要公网可访问，用 Cloudflare Tunnel 已满足
NOTIFY_URL = "https://www.jugongchang.icu/api/alipay/notify"

# ===== 当面付参数 =====
# 支付超时时间（分钟）
TRADE_TIMEOUT_MINUTES = 30
