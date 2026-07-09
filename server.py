import http.server
import json
import urllib.request
import os
import sys
import datetime
from pathlib import Path

PORT = 3722
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 支付宝当面付（可选，无密钥时降级）
try:
    import alipay_service
    ALIPAY_READY = alipay_service.alipay_ready
except ImportError:
    alipay_service = None
    ALIPAY_READY = False
try:
    import qrcode
    from io import BytesIO
    import base64
    QR_READY = True
except ImportError:
    QR_READY = False
API_KEY = os.environ.get("DEEPSEEK_KEY", "")
FREE_DAILY_LIMIT = 2
RATE_LIMIT_FILE = Path(__file__).parent / "rate_limit.json"

# ── Prompt templates ──────────────────────────────────────────

GENRE_CONFIG = {
    "niixi": {"name": "都市逆袭", "desc": "草根逆袭，打脸装逼，爽感拉满"},
    "yanqing": {"name": "甜宠言情", "desc": "霸道总裁/甜宠虐恋，女性向"},
    "xuanyi": {"name": "悬疑惊悚", "desc": "反转再反转，烧脑推理"},
    "chuanyue": {"name": "穿越重生", "desc": "古穿今/今穿古/重生复仇"},
    "tianchong": {"name": "甜宠先婚后爱", "desc": "契约婚姻/先婚后爱，高糖预警"},
}

GENRE_STRUCTURE = {
    "niixi": """
## 短剧风格：都市逆袭爽剧
## 核心要素
- 开头3秒必须有冲突/悬念/打脸
- 每集至少2次情绪反转
- 主角从弱势到强势的升级感
- 平均15-20秒一个爽点
- 结尾必须留钩子（下集预告）
""",
    "yanqing": """
## 短剧风格：甜宠言情
## 核心要素
- 第一秒就建立CP张力
- 甜-虐-甜的节奏感
- 肢体接触/眼神戏/微表情特写密集
- 每集1个名场面（壁咚/求婚/英雄救美）
- 结尾必有矛盾爆发或误会
""",
    "xuanyi": """
## 短剧风格：悬疑惊悚
## 核心要素
- 开局必须有命案/失踪/诡异事件
- 每集至少1个反转
- 线索铺垫与误导并行
- 阴暗压抑的画面氛围
- 结尾留下更大谜团
""",
    "chuanyue": """
## 短剧风格：穿越重生
## 核心要素
- 开局快速交代穿越/重生设定（30秒内）
- 利用现代/前世知识降维打击
- 复仇/逆袭/改变命运主线
- 古今反差制造笑点和爽点
- 每集解决一个前世遗憾
""",
    "tianchong": """
## 短剧风格：甜宠先婚后爱
## 核心要素
- 开场直接进入契约婚姻场景
- 男主高冷女主软萌/女强人
- 假戏真做的渐进感
- 吃醋/护妻/甜蜜同居桥段
- 每集一个心动瞬间
""",
}

EXTRA_STYLES = {
    "hot": "要求：参考当前抖音/快手最火的短剧爆款公式，开头5秒必须有高能钩子，每15秒一个情绪引爆点。参考热门短剧的节奏感。",
    "short": "要求：精简版。每句台词不超过15字，节奏极快，平均8-10秒切换一个场景。镜头语言多用特写和快速切换。",
    "long": "要求：深度剧情版。可以铺垫更长的人物关系和情感线，对白更丰富细腻，单集可扩展至1200-1500字。",
}

SYSTEM_PROMPT = """你是一位专业的AI短剧编剧，精通竖屏短剧的创作规律。你的任务是根据用户提供的题材要求，生成一部适合拍摄的竖屏短剧脚本。

## 短剧黄金法则
1. 竖屏思维：画面以人物半身/特写为主，避免大场景全景
2. 节奏：每15-20秒一个情绪点，每集至少3个高潮点
3. 对白：简洁有力，一句台词不超过20字
4. 爽点密集：打脸、反转、告白、揭秘交替出现
5. 结尾钩子：每集最后一句台词/一个画面必须是悬念

## 输出格式
必须严格按照以下结构输出：

【剧名】
【类型】
【集数】最近1集（约3分钟，800-1000字）
【人物表】列出主要角色及性格标签
【剧情概要】本集100字梗概

【分镜表】
以表格形式输出：镜头序号 | 景别 | 时长(秒) | 画面描述 | 台词 | 音效/BGM

【完整剧本】
以标准剧本格式输出每场戏：场景/人物/对白/动作指示

【下集钩子】结尾悬念提示

请开始创作。"""

# ── HTTP Handlers ──────────────────────────────────────────────

class APIHandler(http.server.BaseHTTPRequestHandler):

    def _send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/genres":
            genres = [{"id": k, "name": v["name"], "desc": v["desc"]} for k, v in GENRE_CONFIG.items()]
            self._send_json(200, {"genres": genres})
        elif self.path == "/api/usage":
            self._handle_usage()
        elif self.path == "/api/alipay/status":
            self._handle_check_subscription()
        elif self.path.startswith("/api/alipay/query?"):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            trade_no = qs.get("trade_no", [None])[0]
            if trade_no:
                self._handle_payment_query(trade_no)
            else:
                self._send_json(400, {"error": "Missing trade_no"})
        elif self.path.startswith("/api/alipay/qrcode"):
            self._handle_qrcode()
        else:
            self._serve_static()

    def do_POST(self):
        if self.path == "/api/generate":
            self._handle_generate()
        elif self.path == "/api/alipay/create":
            self._handle_create_payment()
        elif self.path == "/api/alipay/notify":
            self._handle_alipay_notify()
        else:
            self._send_json(404, {"error": "Not found"})

    def _get_client_ip(self):
        return self.client_address[0]

    def _load_rate_limit(self):
        if RATE_LIMIT_FILE.exists():
            try:
                return json.loads(RATE_LIMIT_FILE.read_text("utf-8"))
            except:
                return {}
        return {}

    def _save_rate_limit(self, data):
        RATE_LIMIT_FILE.write_text(json.dumps(data, ensure_ascii=False), "utf-8")

    def _check_daily_limit(self, ip):
        today = datetime.date.today().isoformat()
        data = self._load_rate_limit()
        key = f"{ip}:{today}"
        used = data.get(key, 0)
        remaining = max(0, FREE_DAILY_LIMIT - used)
        return remaining, used

    def _increment_usage(self, ip):
        today = datetime.date.today().isoformat()
        data = self._load_rate_limit()
        key = f"{ip}:{today}"
        data[key] = data.get(key, 0) + 1
        self._save_rate_limit(data)

    def _handle_usage(self):
        ip = self._get_client_ip()
        remaining, used = self._check_daily_limit(ip)
        self._send_json(200, {
            "plan": "free",
            "daily_limit": FREE_DAILY_LIMIT,
            "used": used,
            "remaining": remaining
        })

    def _handle_generate(self):
        try:
            body = self._read_body()
        except Exception:
            self._send_json(400, {"error": "无效的请求体"})
            return

        genre = body.get("genre", "niixi")
        plot = body.get("plot", "").strip()
        extra = body.get("extra", "hot")
        characters = body.get("characters", "").strip()
        special = body.get("special", "").strip()

        # Check rate limit
        client_ip = self._get_client_ip()
        remaining, used = self._check_daily_limit(client_ip)
        if remaining <= 0:
            self._send_json(429, {"error": f"今日免费次数已用完（{FREE_DAILY_LIMIT}/{FREE_DAILY_LIMIT}），升级专业版可无限使用", "usage": {"plan": "free", "daily_limit": FREE_DAILY_LIMIT, "used": used, "remaining": 0}})
            return

        if not plot:
            self._send_json(400, {"error": "请提供核心梗概"})
            return
        if len(plot) < 5:
            self._send_json(400, {"error": "梗概太短了，请至少输入5个字"})
            return

        genre_name = GENRE_CONFIG.get(genre, {}).get("name", "自定义")
        genre_struct = GENRE_STRUCTURE.get(genre, "")
        extra_prompt = EXTRA_STYLES.get(extra, EXTRA_STYLES["hot"])
        chars = characters if characters else "由AI根据题材自动生成"
        sp = special if special else "无"

        user_prompt = f"""请为我创作一部短剧脚本。

## 题材
{genre_name}

## 核心梗概
{plot}

## 关键要求
{extra_prompt}

## 人物设定
{chars}

## 特殊要求
{sp}"""

        # Call DeepSeek API
        if not API_KEY:
            self._send_json(200, {
                "success": True,
                "data": {
                    "script": f"""⚠️ API 密钥未配置

请设置环境变量 DEEPSEEK_KEY 后重新生成。

你输入的梗概为：
{plot}

题材：{genre_name}

当前为演示模式，配置 API Key 后即可正常使用。

配置方法：
1. 注册 DeepSeek 官网获取 API Key（deepseek.com）
2. 设置环境变量 DEEPSEEK_KEY=your_key_here
3. 重启服务

DeepSeek V4 API 价格：输入 ¥2/百万tokens，输出 ¥6/百万tokens
单次生成成本不到 ¥0.01""",
                    "usage": {"input_tokens": 0, "output_tokens": 0, "estimated_cost": 0}
                }
            })
            return

        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + genre_struct},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 4096,
            "stream": False
        }).encode("utf-8")

        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_text = e.read().decode("utf-8", errors="replace")
            self._send_json(e.code, {"error": f"API请求失败: {err_text}"})
            return
        except urllib.error.URLError as e:
            self._send_json(502, {"error": f"无法连接DeepSeek API: {e.reason}"})
            return
        except Exception as e:
            self._send_json(500, {"error": f"请求异常: {str(e)}"})
            return

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Deduct one usage on success
        self._increment_usage(client_ip)
        usage = data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        estimated_cost = (output_tokens / 1000000) * 6 + (input_tokens / 1000000) * 2

        self._send_json(200, {
            "success": True,
            "data": {
                "script": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "estimated_cost": round(estimated_cost, 6)
                }
            }
        })

    def _serve_static(self):
        public_dir = Path(__file__).parent / "public"
        # Default to index.html
        path = self.path.lstrip("/")
        if not path or path == "/":
            path = "index.html"
        
        file_path = public_dir / path
        
        # Security: prevent directory traversal
        try:
            file_path = file_path.resolve()
            if not str(file_path).startswith(str(public_dir.resolve())):
                self._send_json(403, {"error": "Forbidden"})
                return
        except Exception:
            self._send_json(403, {"error": "Forbidden"})
            return

        if not file_path.exists() or not file_path.is_file():
            # Custom 404 page
            file_path = public_dir / "404.html"
            if not file_path.exists():
                self._send_json(404, {"error": "Not found"})
                return

        mime_map = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
        }
        ext = file_path.suffix.lower()
        content_type = mime_map.get(ext, "application/octet-stream")

        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

    # ── 支付宝支付接口 ──────────────────────────────────────────

    def _handle_create_payment(self):
        from urllib.parse import urlparse, parse_qs
        body = self._read_body()
        plan_id = body.get("plan_id", "")
        if plan_id not in ("pro_monthly", "studio_monthly"):
            self._send_json(400, {"error": "无效套餐"})
            return
        result = alipay_service.create_qr_payment(plan_id)
        if result.get("success"):
            self._send_json(200, {
                "success": True,
                "qr_code": result["qr_code"],
                "out_trade_no": result["out_trade_no"],
                "total_amount": result["total_amount"],
                "plan_name": alipay_service.PLANS[plan_id]["name"],
            })
        else:
            self._send_json(500, {"success": False, "error": result.get("error", "支付创建失败")})

    def _handle_payment_query(self, out_trade_no):
        result = alipay_service.query_payment(out_trade_no)
        self._send_json(200, result)

    def _handle_alipay_notify(self):
        """支付宝异步通知回调"""
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        # 支付宝 POST 是 form-encoded
        from urllib.parse import parse_qs
        data = {k: v[0] for k, v in parse_qs(raw).items()}

        if alipay_service.verify_notification(data):
            trade_status = data.get("trade_status", "")
            out_trade_no = data.get("out_trade_no", "")
            if trade_status == "TRADE_SUCCESS":
                # 提取 plan_id 从 out_trade_no (jgc_时间戳_pro_monthly)
                parts = out_trade_no.split("_")
                plan_id = parts[-1] if len(parts) >= 3 else "pro_monthly"
                alipay_service.activate_subscription(
                    out_trade_no, plan_id, data.get("buyer_id", "unknown")
                )
                print(f"[ALIPAY] 订阅激活成功: {out_trade_no} ({plan_id})")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"success")
        else:
            print(f"[ALIPAY] 通知验签失败: {data}")
            self.send_response(403)
            self.end_headers()

    def _handle_qrcode(self):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(self.path).query)
        data = qs.get("data", [None])[0]
        if not data:
            self._send_json(400, {"error": "Missing data param"})
            return
        if not QR_READY:
            self._send_json(500, {"error": "QR module not available"})
            return
        img = qrcode.make(data)
        buf = BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        self._send_json(200, {"success": True, "qr_base64": b64})

    def _handle_check_subscription(self):
        """检查当前用户的订阅状态"""
        ip = self._get_client_ip()
        premium = alipay_service.is_premium(ip)
        expiry = alipay_service.get_expiry(ip)
        self._send_json(200, {"premium": premium, "expires_at": expiry})


# ── Main ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    status = 'OK' if API_KEY else 'NOT SET (dev mode)'
    print('=' * 45)
    print('|  JuGongChang - AI Duanju Script Generator  |')
    print('|                                            |')
    print(f'|  http://localhost:{PORT:<26}|')
    print('|                                            |')
    print(f'|  DeepSeek Key: {status:<21}|')
    print('=' * 45)
    print()
    
    server = http.server.HTTPServer(("0.0.0.0", PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
        server.server_close()
