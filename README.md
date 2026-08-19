# 剧工厂 - AI短剧脚本生成器

> 🎬 输入一句话，30秒生成爆款短剧脚本

**在线体验：** https://ugo2000.github.io/ai-script-hub/

## 功能

- ✅ 5种热门题材：都市逆袭、甜宠言情、悬疑惊悚、穿越重生、先婚后爱
- ✅ 3种节奏风格：爆款节奏、快节奏、深度剧情
- ✅ 自动分镜表 + 完整剧本 + 下集钩子
- ✅ 用户注册 / 登录
- ✅ 免费版每日2次，专业版无限次
- ✅ 支付宝/微信支付开通专业版

## 技术栈

- **前端**：纯 HTML/CSS/JS（静态站点，GitHub Pages 托管）
- **数据库 + 认证**：Supabase（PostgreSQL + Auth）
- **AI 生成**：DeepSeek API（前端直调）
- **支付**：支付宝当面付 / 微信支付（接入中）

## 本地开发

```bash
# 直接用浏览器打开
open public/index.html

# 或用简单 HTTP 服务器
python3 -m http.server 8080
# 访问 http://localhost:8080
```

## 配置说明

首次使用需要在 `public/index.html` 的 JS 部分（顶部）配置：

```javascript
const SUPABASE_URL = 'https://你的项目.supabase.co';
const SUPABASE_ANON_KEY = '你的anon-key';
const DEEPSEEK_API_KEY = '你的DeepSeek-API-Key';
```

然后在 Supabase SQL Editor 中运行 `supabase/schema.sql` 创建数据表。

## 部署

推送到 GitHub 后自动部署到 GitHub Pages：
https://ugo2000.github.io/ai-script-hub/

## 版权

© 2026 剧工厂 · 让每个人都能成为短剧编剧
