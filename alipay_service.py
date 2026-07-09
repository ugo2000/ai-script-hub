# -*- coding: utf-8 -*-
"""
支付宝当面付 — 扫码支付模块
接口：alipay.trade.precreate（生成付款二维码）
文档：https://opendocs.alipay.com/open/194/106078
"""
import json, logging, time
from alipay import AliPay

# 只在有密钥文件时加载配置
alipay = None
alipay_ready = False

try:
    from alipay_config import ALIPAY_APP_ID, APP_PRIVATE_KEY_PATH, ALIPAY_PUBLIC_KEY, NOTIFY_URL, TRADE_TIMEOUT_MINUTES

    with open(APP_PRIVATE_KEY_PATH, "r", encoding="utf-8") as f:
        app_private_key = f.read()

    alipay = AliPay(
        appid=ALIPAY_APP_ID,
        app_notify_url=NOTIFY_URL,
        app_private_key_string=app_private_key,
        alipay_public_key_string=ALIPAY_PUBLIC_KEY,
        sign_type="RSA2",
        debug=False,
    )
    alipay_ready = True
    logging.info("✅ 支付宝当面付初始化成功")
except FileNotFoundError as e:
    logging.warning(f"⚠️ 支付宝密钥文件未就绪: {e}")
except Exception as e:
    logging.warning(f"⚠️ 支付宝初始化失败: {e}")


# ===== 定价方案 =====
PLANS = {
    "pro_monthly": {
        "name": "剧工厂专业版 - 月付",
        "price": 39.00,  # 元
        "days": 30,
    },
    "studio_monthly": {
        "name": "剧工厂工作室版 - 月付",
        "price": 199.00,
        "days": 30,
    },
}


def create_qr_payment(plan_id: str, out_trade_no: str = None) -> dict:
    """
    生成付款二维码
    返回: {"success": bool, "qr_code": "https://...", "trade_no": "..."}
    """
    if not alipay_ready:
        return {"success": False, "error": "支付系统未就绪"}

    plan = PLANS.get(plan_id)
    if not plan:
        return {"success": False, "error": f"未知套餐: {plan_id}"}

    if not out_trade_no:
        out_trade_no = f"jgc_{int(time.time())}_{plan_id}"

    # 金额转元 -> 分（alipay-sdk 要求元为单位）
    total_amount = plan["price"]

    order_string = alipay.api_alipay_trade_precreate(
        subject=plan["name"],
        out_trade_no=out_trade_no,
        total_amount=total_amount,
        timeout_express=f"{TRADE_TIMEOUT_MINUTES}m",
    )

    # order_string 是 dict
    if order_string.get("code") == "10000":
        return {
            "success": True,
            "qr_code": order_string.get("qr_code"),
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
        }
    else:
        return {
            "success": False,
            "error": order_string.get("sub_msg", order_string.get("msg", "未知错误")),
        }


def query_payment(out_trade_no: str) -> dict:
    """查询交易状态"""
    if not alipay_ready:
        return {"success": False, "error": "支付系统未就绪"}

    result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
    if result.get("code") == "10000":
        trade_status = result.get("trade_status", "")
        return {
            "success": True,
            "trade_status": trade_status,
            "paid": trade_status == "TRADE_SUCCESS",
            "buyer_id": result.get("buyer_user_id", ""),
            "receipt_amount": result.get("receipt_amount", "0"),
            "gmt_payment": result.get("send_pay_date", ""),
        }
    else:
        return {
            "success": False,
            "error": result.get("sub_msg", result.get("msg", "查询失败")),
        }


def verify_notification(data: dict) -> bool:
    """验证支付宝异步通知签名"""
    if not alipay_ready:
        return False
    # data 就是支付宝 POST 过来的 dict
    signature = data.pop("sign", "")
    return alipay.verify(data, signature)


def cancel_order(out_trade_no: str) -> dict:
    """关闭未支付订单"""
    if not alipay_ready:
        return {"success": False, "error": "支付系统未就绪"}
    result = alipay.api_alipay_trade_close(out_trade_no=out_trade_no)
    return {"success": result.get("code") == "10000", "msg": result.get("sub_msg", "")}


# ===== 用户订阅管理（内存/文件版，正式应该用数据库）=====
import json, os, datetime
from pathlib import Path

SUBS_FILE = Path(__file__).parent / "subscriptions.json"

def _load_subs() -> dict:
    if SUBS_FILE.exists():
        try:
            return json.loads(SUBS_FILE.read_text("utf-8"))
        except:
            return {}
    return {}

def _save_subs(data: dict):
    SUBS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")

def activate_subscription(out_trade_no: str, plan_id: str, ip: str) -> dict:
    """激活订阅"""
    plan = PLANS.get(plan_id)
    if not plan:
        return {"success": False, "error": "无效套餐"}
    subs = _load_subs()
    now = datetime.datetime.utcnow()
    expires = now + datetime.timedelta(days=plan["days"])
    subs[out_trade_no] = {
        "plan_id": plan_id,
        "plan_name": plan["name"],
        "ip": ip,
        "activated_at": now.isoformat() + "Z",
        "expires_at": expires.isoformat() + "Z",
    }
    _save_subs(subs)
    return {"success": True, "expires_at": expires.isoformat() + "Z"}

def is_premium(ip: str) -> bool:
    """检查 IP 是否为专业版用户"""
    subs = _load_subs()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    for trade_no, sub in subs.items():
        if sub.get("ip") == ip and sub.get("expires_at", "") > now:
            return True
    return False

def get_expiry(ip: str) -> str:
    """获取订阅到期时间"""
    subs = _load_subs()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    for trade_no, sub in subs.items():
        if sub.get("ip") == ip and sub.get("expires_at", "") > now:
            return sub.get("expires_at", "")
    return ""
