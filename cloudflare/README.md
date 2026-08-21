# 剧工厂 · 支付宝当面付（Cloudflare Worker）

专业版（¥39/月）收款通道。前端扫码 → Worker 调支付宝生成订单 → 用户付款 → 支付宝回调 Worker 验签 → 自动把 Supabase 会员升级为 `premium`。

## 1. 部署 Worker

**方式 A：Cloudflare 控制台（推荐，零命令行）**
1. Cloudflare 控制台 → **Workers & Pages** → **创建** → 选 "Create Worker"
2. 名称随意（如 `jugong-pay`），把 `payment-worker.js` 全文粘贴进去，点 **Deploy**
3. 部署后得到地址 `https://jugong-pay.<你的子域>.workers.dev`
4. （可选）绑定自定义域：Workers → 该 Worker → **Settings → Triggers → Custom Domains** → 添加 `pay.jugongchang.icu`
   - 之后把前端 `index.html` 里的 `PAY_WORKER` 改成 `https://pay.jugongchang.icu`
   - 没绑自定义域就用 `https://jugong-pay.<子域>.workers.dev`

**方式 B：wrangler**
```
wrangler deploy
```

## 2. 配置 6 个 Secret（Settings → Variables → Add variable，每个都点 "Encrypt" / Add secret）

| 变量名 | 内容 |
|---|---|
| `ALIPAY_APP_ID` | 支付宝当面付应用 APPID（如 `2021006170643597`） |
| `ALIPAY_APP_PRIVATE_KEY` | 应用私钥（PKCS8 PEM，含 `-----BEGIN/END-----` 和换行） |
| `ALIPAY_PUBLIC_KEY` | **支付宝公钥**（SPKI PEM；注意是"支付宝公钥"，不是你上传的应用公钥） |
| `ALIPAY_NOTIFY_URL` | Worker 的 `/notify` 完整地址，如 `https://pay.jugongchang.icu/notify` |
| `SUPABASE_URL` | `https://mqvygeoqjfylgdmklvrb.supabase.co` |
| `SUPABASE_SERVICE_ROLE` | Supabase 控制台 → Project Settings → API → `service_role` key |

> wrangler 方式用：`wrangler secret put ALIPAY_APP_ID` 逐个添加。

## 3. 支付宝后台配置

1. 支付宝开放平台 → 你的应用（当面付）→ **开发设置** → **授权回调地址 / 应用网关 / 公钥**
2. 把 **`ALIPAY_NOTIFY_URL`** 填到「异步通知地址（notify_url）」
3. 确认「支付宝公钥」已配置（用于验签，对应上面的 `ALIPAY_PUBLIC_KEY`）
4. 确认应用已「签约当面付」且状态正常

## 4. 前端

`index.html` 里 `const PAY_WORKER = 'https://pay.jugongchang.icu';` 改成你的 Worker 地址即可。

## 校验流程

- 前端 `openPay('premium')` → `POST {WORKER}/create` → 返回 `{qr}`（支付宝订单码）
- 前端用 qrserver 把 `qr` 渲染成二维码图片展示
- 用户支付宝扫码付款 → 支付宝 POST `{WORKER}/notify`
- Worker 验签 → `PATCH profiles set plan='premium' where id={uid}`
- 前端每 3 秒轮询自己 `profiles.plan`，变 `premium` 即提示开通成功
