# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.chdir("C:\\Users\\Administrator\\.qclaw\\workspace\\ai-script-hub")
from Crypto.PublicKey import RSA
key = RSA.generate(2048)
private = key.export_key("PEM").decode()
public = key.publickey().export_key("PEM").decode()
with open("app_private_key.pem", "w", encoding="utf-8") as f:
    f.write(private)
with open("app_public_key.pem", "w", encoding="utf-8") as f:
    f.write(public)
print("=== GENERATED OK ===")
print()
print("---APP PUBLIC KEY (复制到支付宝 -> 接口加签)---")
print(public)
print("---END---")
