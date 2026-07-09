# test_alipay.py
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(os.path.dirname(__file__) or ".")
import alipay_service
print("ready:", alipay_service.alipay_ready)
r = alipay_service.create_qr_payment('pro_monthly')
print("result:", r)
